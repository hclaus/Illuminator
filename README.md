# Illuminator

A Tkinter GUI for controlling a 4-channel OSLUV lamp fixture over serial/UART. The GUI was built with [PAGE](http://page.sourceforge.net/) (Tcl/Tk GUI designer) and runs on a Raspberry Pi 5 or on Windows, talking to each lamp's controller board over its own UART.

## Files

| File | Purpose |
|---|---|
| `ScreenV1.py` / `ScreenV1.tcl` | PAGE-generated GUI definition (widgets, layout). |
| `ScreenV1_support.py` | App entry point (`main`) and widget callbacks (lamp on/off buttons, dim-level listboxes, "check for lamps"). |
| `Pi_support.py` | Serial/UART layer: opens the lamp ports, sends/reads commands, and pushes status back into the GUI. |
| `main.py` | Standalone UART read/write test script (not used by the GUI). |
| `serial commands OSLUV controller V1.docx` | Serial command protocol reference for the lamp controller boards. |

## Hardware

- Raspberry Pi 5
    - 4 independent UARTs, one per lamp
    - [RP5 UART hardware notes](https://github.com/user-attachments/files/25348169/RP5.UART.hardware.docx)

- Windows
    - needs a USB to 4xUART controller
## Serial protocol (summary)

Each lamp is addressed over its own serial port at 9600 baud. Commands/responses are `\n`-terminated, colon-delimited:

- `S:L:<0|1>` — set lamp off/on
- `S:D:<20|40|70|100>` — set dim level (%)
- `G:L` — get lamp on/off status
- `G:D` — get dim level
- No response within the read timeout is treated as `:::No Lamp found`, which disables that lamp's controls in the GUI.

See `serial commands OSLUV controller V1.docx` for the full command set.

## Running

```bash
python ScreenV1.py
```

On startup, `Pi_support.InitUarts()` opens the expected serial ports:

- **Linux (Raspberry Pi):** `/dev/ttyAMA4`, `/dev/ttyAMA1`, `/dev/ttyAMA2`, `/dev/ttyAMA3`
- **Windows (dev/test):** `COM7`, `COM8`, `COM6`, `COM5`

Adjust the port lists in `InitUarts()` to match your hardware. A port that fails to open is left as `None` and that lamp's controls are disabled rather than crashing the app.

Shortly after the window opens, `Pi_support.RefreshLampStatus()` runs (via `root.after`) and queries `G:L` and `G:D` for all 4 lamps, so each lamp's on/off button text and dim-level listbox selection reflect real hardware state at launch rather than defaulting to "off". The same function backs the "check for lamps" button (`UART_checkforLamps`), so it re-syncs status and dim level on demand too. It's called after the widgets are built (not from `InitUarts()`), since it writes directly into `_w1` widgets that don't exist yet at that point.

## Notes

- `backups/` and the VS Code/Visual Studio metadata folders (`.vs/`, `__pycache__/`) are not tracked in git.
- The `backup-remote-main-20261013` branch preserves an earlier, alternate UART-init implementation (`get_uarts()`/`StartPi()`) that was superseded by `InitUarts()` on `main`.

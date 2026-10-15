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

### Configuring the lamp ports (`Port_List`)

On startup, `Pi_support.InitUarts()` reads the serial port for each lamp from a `Port_List` file in the same folder as the running app (next to the `.exe`, or next to `Pi_support.py` when run from source/`.bat`). If that file doesn't exist yet, it's created automatically with a platform-appropriate example:

```
# Port_List - serial port for each lamp, one per line, in order 1-4
# Windows example: COM5        Linux example: /dev/ttyAMA1
COM7
COM8
COM6
COM5
```

Edit the four port lines to match your actual hardware (e.g. whatever COM ports your USB-to-UART adapter enumerates as) and restart the app — no rebuild needed. Blank lines and lines starting with `#` are ignored. If fewer than 4 ports are listed, the remaining lamp slots are simply left disabled rather than falling back to a default. A port that fails to open is also left as `None`, disabling that lamp's controls instead of crashing the app. `Port_List` is machine-specific and isn't tracked in git.

Shortly after the window opens, `Pi_support.RefreshLampStatus()` runs (via `root.after`) and queries `G:L` and `G:D` for all 4 lamps, so each lamp's on/off button text and dim-level listbox selection reflect real hardware state at launch rather than defaulting to "off". The same function backs the "check for lamps" button (`UART_checkforLamps`), so it re-syncs status and dim level on demand too. 

## Notes

- `backups/` and the VS Code/Visual Studio metadata folders (`.vs/`, `__pycache__/`) are not tracked in git.
- The `backup-remote-main-20261013` branch preserves an earlier, alternate UART-init implementation (`get_uarts()`/`StartPi()`) that was superseded by `InitUarts()` on `main`.

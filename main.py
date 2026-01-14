import serial
import threading
# adjust to the actual device names you see in /dev
uart0 = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=0.1)
uart1 = serial.Serial("/dev/ttyAMA1", baudrate=115200, timeout=0.1)
uart2 = serial.Serial("/dev/ttyAMA2", baudrate=115200, timeout=0.1)
uart3 = serial.Serial("/dev/ttyAMA3", baudrate=115200, timeout=0.1)
# uart4 = serial.Serial("/dev/ttyAMA4", baudrate=115200, timeout=0.1)

uarts = [uart0, uart1, uart2, uart3]

#setup event readers for each UART

def make_on_line(name):
    def on_line(line: str):
        print(f"{name}: {line}")
        # put your per-UART logic here
    return on_line

def reader(uarts: serial.Serial, name: str):
    buf = b""
    on_line = make_on_line(name)
    while True:
        chunk = uarts.read(1024)
        if not chunk:
            continue
        buf += chunk
        while b"\n" in buf:
            line, _, buf = buf.partition(b"\n")
            on_line(line.decode(errors="ignore"))

serial_objs = []
threads = []

for i, dev in enumerate(uarts):
    #ser = serial.Serial(dev, 115200, timeout=0.1)
    serial_objs.append(dev)
    t = threading.Thread(
        target=reader,
        args=(dev, f"UART{i}"),
        daemon=True,
    )
    t.start()
    threads.append(t)

while True:
    for idx, ser in enumerate(uarts):
        ser.write(f"Ping from UART{idx}\n".encode())
        # data = ser.readline()
        # if data:
        #     print(f"UART{idx} RX:", data.decode(errors="ignore").strip())







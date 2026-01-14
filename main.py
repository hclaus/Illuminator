import serial

# adjust to the actual device names you see in /dev
uart0 = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=0.1)
uart1 = serial.Serial("/dev/ttyAMA1", baudrate=115200, timeout=0.1)
uart2 = serial.Serial("/dev/ttyAMA2", baudrate=115200, timeout=0.1)
uart3 = serial.Serial("/dev/ttyAMA3", baudrate=115200, timeout=0.1)
# uart4 = serial.Serial("/dev/ttyAMA4", baudrate=115200, timeout=0.1)

uarts = [uart0, uart1, uart2, uart3]

while True:
    for idx, ser in enumerate(uarts):
        ser.write(f"Ping from UART{idx}\n".encode())
        data = ser.readline()
        if data:
            print(f"UART{idx} RX:", data.decode(errors="ignore").strip())

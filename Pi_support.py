#contain code that deals with RP5 UART communication and related screen updates

from gc import enable
import sys
import os
import ScreenV1_support
import ScreenV1
#import threading
import serial
import ScreenV1_support
import platform
_debug=True
_RPpresent=True
_postMsg=True
_Simdevice=False #this doesn't work yet

print("__name__:", __name__)

# add near top of file (replace the top-level open)
_uarts_initialized = False
uarts = []

PORT_LIST_FILENAME = "Port_List"

def _app_dir():
    """Folder the exe (or .py/.bat) lives in, so Port_List sits next to it."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def _default_ports():
    if platform.system() == "Windows":
        return ["COM7", "COM8", "COM6", "COM5"]
    return ["/dev/ttyAMA4", "/dev/ttyAMA1", "/dev/ttyAMA2", "/dev/ttyAMA3"]

def _load_port_list():
    """Read lamp 1-4 ports from Port_List next to the app, creating a default example if missing."""
    path = os.path.join(_app_dir(), PORT_LIST_FILENAME)
    defaults = _default_ports()

    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write("# Port_List - serial port for each lamp, one per line, in order 1-4\n")
            f.write("# Windows example: COM5        Linux example: /dev/ttyAMA1\n")
            for p in defaults:
                f.write(p + "\n")
        if _debug: print("Created default Port_List at", path)
        return defaults

    ports = []
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            ports.append(line)

    ports = ports[:4]
    while len(ports) < 4:
        ports.append(None)  # lamp slot left unconfigured, stays disabled
    if _debug: print("Loaded ports from", path, ":", ports)
    return ports

def InitUarts(port_list=None, baud=9600, timeout=1, map_single_to_all=False):
    """
    Initialize expected UART ports.
    - If port_list is None, read lamps 1-4's ports from the Port_List file (created with
      platform defaults on first run if it doesn't exist yet).
    - If map_single_to_all True and exactly one port opened, replicate it for 4 lamp indices (testing).
    """
    global uarts, _uarts_initialized, _RPpresent
    if _uarts_initialized:
        return

    if port_list is None:
        port_list = _load_port_list()

    uarts = []
    for p in port_list:
        if p is None:
            uarts.append(None)
            continue
        try:
            ser = serial.Serial(p, baudrate=baud, timeout=timeout)
            uarts.append(ser)
            if _debug: print("Opened", p)
        except Exception as e:
            uarts.append(None)
            if _debug: print("Failed to open", p, repr(e))

    # optional short-circuit for single-port Windows test
    non_none_ports = [s for s in uarts if s is not None]
    if map_single_to_all and len(non_none_ports) == 1:
        uarts = [non_none_ports[0]] * 4
        if _debug: print("Mapped single opened port to 4 lamp slots for testing")

    _uarts_initialized = True
    _RPpresent = any(x is not None for x in uarts)

def RefreshLampStatus():
    for i in range(4):
        lamp = i + 1
        msg = SendUART(lamp, 'G:L')  #drives SetGet -> updates TbLampOn*.text
        if msg == ':::No Lamp found':
            if _debug:
                print('No response from Lamp', lamp)
            DisableFrame(lamp)
            continue  #skip G:D, nothing listens on this port
        EnableFrame(lamp)
        SendUART(lamp, 'G:D')  #drives SetGet -> updates Listbox* selection

def UART_checkforLamps():
    RefreshLampStatus()


def DisableFrame(lamp):
    match lamp:
        case 1:
            ScreenV1_support.disable_frame_children(ScreenV1_support._w1.TFrame1)
        case 2:
            ScreenV1_support.disable_frame_children(ScreenV1_support._w1.TFrame2)
        case 3:
            ScreenV1_support.disable_frame_children(ScreenV1_support._w1.TFrame3)       
        case 4:
            ScreenV1_support.disable_frame_children(ScreenV1_support._w1.TFrame4)

def EnableFrame(lamp):
    match lamp:
        case 1:
            ScreenV1_support.enable_frame_children(ScreenV1_support._w1.TFrame1)
        case 2:
            ScreenV1_support.enable_frame_children(ScreenV1_support._w1.TFrame2)
        case 3:
            ScreenV1_support.enable_frame_children(ScreenV1_support._w1.TFrame3)       
        case 4:
            ScreenV1_support.enable_frame_children(ScreenV1_support._w1.TFrame4)

    # def make_on_line(name):
    #     def on_line(line: str):
    #         print(f"from event: {name}: {line}")
    #         if _Simdevice:
    #             line=line+':OK' # simulate board response

    #         ReadUART(int(name), line)
    #     return on_line

    # def reader(uarts: serial.Serial, name: str):
    #     buf = b""
    #     on_line = make_on_line(name)
    #     while True:
    #         chunk = uarts.read(1024)
    #         if not chunk:
    #             continue
    #         buf += chunk
    #         while b"\n" in buf:
    #             line, _, buf = buf.partition(b"\n")
    #             on_line(line.decode(errors="ignore"))

    # serial_objs = []
    # threads = []

    # def SetupUARTReaders():

    #     for i, dev in enumerate(uarts):
    #         #ser = serial.Serial(dev, 115200, timeout=0.1)
    #         serial_objs.append(dev)
    #         t = threading.Thread(
    #             target=reader,
    #             args=(dev, f"{i}"),
    #             #args=(dev, f"UART{i}"),
    #             daemon=True,
    #         )
    #         t.start()
    #         threads.append(t)

def SetLamp(lamp,option): #on/off
    print("Lamp:", {lamp}, "Option:" ,{str(option)})
    #code for UART
    txt='S:L:'+str(option)
    SendUART(lamp,txt)

def SetDim(lamp,option):
    if option==0:
        level='20'
    if option==1:
        level='40'
    if option==2:
        level='70'
    if option==3:
        level='100'    
    txt='S:D:'+level
    SendUART(lamp,txt)

def SendUART(lamp, txt):
    idx = lamp - 1
    if idx < 0 or idx >= len(uarts):
        if _debug: print("Invalid lamp index:", lamp)
        return ":::No Lamp found"
    port = uarts[idx]
    if port is None:
        if _debug: print("No serial port for lamp", lamp)
        return ":::No Lamp found"

    port.write((txt + '\n').encode('utf-8'))
    if _debug:
        print('Lamp', lamp, 'Text:', txt)
    sys.stdout.flush()
    return ReadUART(lamp)

def ReadUART(lamp: int):
    idx = lamp - 1
    if idx < 0 or idx >= len(uarts) or uarts[idx] is None:
        msg = ':::No Lamp found'
        if _postMsg:
            PostMsg(lamp, msg)
        return msg

    msg = uarts[idx].readline().decode('utf-8', errors='ignore').rstrip('\r\n')
    if msg == '':
        msg = ':::No Lamp found'
    if _postMsg:
        PostMsg(lamp,msg)
    
    msgArr=msg.split(':')
    if len(msgArr)==4:
        PostError(lamp, msgArr[3])
    if _debug:
        print ('Reading from UART:',msg)
    
    SetGet(lamp,msgArr)
    return msg
    #if msgArr[0]==b'G':

    
    #return msg
   
    
   # set the screen controls based on UART read
def SetGet(lamp,msgArr):
    if len(msgArr) < 3:
        if _debug:
            print('SetGet: unexpected msgArr:', msgArr)
        return
    if msgArr[1]=='L':
        if _debug:
            print ('Get Lamp Status for Lamp:',{lamp+1},'Status:',{msgArr[2]})
        Lcode=msgArr[2]
        if Lcode=='1':
            txt='Turn lamp Off'
        else:
            txt='Turn lamp On'
        match lamp:
            case 1:
                ScreenV1_support._w1.TbLampOn1.configure(text=txt)
            case 2:
                ScreenV1_support._w1.TbLampOn2.configure(text=txt)
            case 3:
                ScreenV1_support._w1.TbLampOn3.configure(text=txt)
            case 4:
                ScreenV1_support._w1.TbLampOn4.configure(text=txt)   
    if msgArr[1]=='D':
        Dcode=msgArr[2]
        match Dcode:
            case '20':
                dimlevel=0
            case '40':
                dimlevel=1
            case '70':
                dimlevel=2
            case '100':
                dimlevel=3  
        match lamp:
            case 1:
                ScreenV1_support._w1.Listbox1.selection_clear(0,ScreenV1_support.tk.END)
                ScreenV1_support._w1.Listbox1.selection_set(dimlevel)
            case 2:
                ScreenV1_support._w1.Listbox2.selection_clear(0,ScreenV1_support.tk.END)
                ScreenV1_support._w1.Listbox2.selection_set(dimlevel)      
            case 3:
                ScreenV1_support._w1.Listbox3.selection_clear(0,ScreenV1_support.tk.END)
                ScreenV1_support._w1.Listbox3.selection_set(dimlevel)  
            case 4:
                ScreenV1_support._w1.Listbox4.selection_clear(0,ScreenV1_support.tk.END)
                ScreenV1_support._w1.Listbox4.selection_set(dimlevel)  

        if _debug:
            print ('Get Dim Level for Lamp:',{lamp+1},'Level:',{msgArr[2]})       

def PostMsg(lamp,msg):
    match lamp:
        case 1:
            ScreenV1_support._w1.StatusvarL11.set(msg)
        case 2:    
            ScreenV1_support._w1.StatusvarL21.set(msg)
        case 3:   
            ScreenV1_support._w1.StatusvarL31.set(msg)      
        case 4:   
            ScreenV1_support._w1.StatusvarL41.set(msg)  


def PostError(lamp,err): 
    match lamp:
        case 1:
            ScreenV1_support._w1.StatusvarL12.set(err)
        case 2:    
            ScreenV1_support._w1.StatusvarL22.set(err)
        case 3:   
            ScreenV1_support._w1.StatusvarL32.set(err)      
        case 4:   
            ScreenV1_support._w1.StatusvarL42.set(err)     


if __name__ == '__main__':
    ScreenV1.start_up()
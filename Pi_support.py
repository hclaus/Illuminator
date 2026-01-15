
import sys
import ScreenV1_support
#import ScreenV1 
import threading

import ScreenV1_support
_debug=True
_RPpresent=True
_postMsg=True
_Simdevice=False #this doesn't work yet

import serial

if _RPpresent:
# adjust to the actual device names you see in /dev
    uart0 = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=0.1)
    uart1 = serial.Serial("/dev/ttyAMA1", baudrate=115200, timeout=0.1)
    uart2 = serial.Serial("/dev/ttyAMA2", baudrate=115200, timeout=0.1)
    uart3 = serial.Serial("/dev/ttyAMA3", baudrate=115200, timeout=0.1)
    #uart4 = serial.Serial("/dev/ttyAMA4", baudrate=115200, timeout=0.1)

    uarts = [uart0, uart1, uart2, uart3]


def make_on_line(name):
    def on_line(line: str):
        print(f"from event: {name}: {line}")
        ReadUART(int(name), line)
        if _Simdevice:
            line=line+':OK'
            SendUART(int(name), line)
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

def SetupUARTReaders():

    for i, dev in enumerate(uarts):
        #ser = serial.Serial(dev, 115200, timeout=0.1)
        serial_objs.append(dev)
        t = threading.Thread(
            target=reader,
            args=(dev, f"{i}"),
            #args=(dev, f"UART{i}"),
            daemon=True,
        )
        t.start()
        threads.append(t)

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
   
    uarts[lamp-1].write((txt+'\n').encode('utf-8'))

    if _debug:
        print ('Lamp',{lamp},'Text:',{txt})
   # uarts[lamp].write((txt+'\n').encode('utf-8'))
    sys.stdout.flush()
    

def ReadUART(lamp:int,msg:str):
    # if lamp==1:
    #     UART='UART1'
    # if lamp==2:
    #     UART='UART2'
    # if lamp==3:
    #     UART='UART3'
    # if lamp==4:
    #     UART='UART4'
   # msg=uarts[lamp-1].readline()
    if _postMsg:
        PostMsg(lamp,msg)

    msgArr=msg.split(':')
    if msgArr[len(msgArr)-1]=="OK":
        PostError(lamp, "OK")
    if _debug:
        print ('Reading from UART:',msg)
    #if msgArr[0]==b'G':

    SetGet(lamp,msgArr)
    return msg
    # else:   
    #     return b'Error'  

    
    
   # set the screen controls based on UART read
def SetGet(lamp,msgArr):
    if msgArr[1]=='L':
        if _debug:
            print ('Get Lamp Status for Lamp:',{lamp+1},'Status:',{msgArr[2]})
            Lcode=msgArr[2]
        if Lcode=='1':
            txt='Turn lamp Off'
        else:
            txt='Turn lamp On'
        match lamp+1:
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
        match lamp+1:
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
    match lamp+1:
        case 1:
            ScreenV1_support._w1.StatusvarL11.set(msg)
        case 2:    
            ScreenV1_support._w1.StatusvarL21.set(msg)
        case 3:   
            ScreenV1_support._w1.StatusvarL31.set(msg)      
        case 4:   
            ScreenV1_support._w1.StatusvarL41.set(msg)  


def PostError(lamp,err): 
    match lamp+1:
        case 1:
            ScreenV1_support._w1.StatusvarL12.set(err)
        case 2:    
            ScreenV1_support._w1.StatusvarL22.set(err)
        case 3:   
            ScreenV1_support._w1.StatusvarL32.set(err)      
        case 4:   
            ScreenV1_support._w1.StatusvarL42.set(err)     
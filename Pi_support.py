#contain code that deals with RP5 UART communication and related screen updates

from gc import enable
import sys
import ScreenV1_support
import ScreenV1 
import threading
import platform

import ScreenV1_support
_debug=True
_RPpresent=True
_postMsg=True
_Simdevice=False #this doesn't work yet

import serial
import serial.tools.list_ports

def get_uarts():
    """Returns [uart0, uart1, uart2, uart3] - identical on Linux/Windows"""
    
    # Your exact Linux ports for Pi 5
    linux_ports = ["/dev/ttyAMA0", "/dev/ttyAMA1", "/dev/ttyAMA2", "/dev/ttyAMA3"]
    
    # Auto-detect available ports first
    available_ports = [p.device for p in serial.tools.list_ports.comports()]
    print("Available ports:", available_ports)
    
    if 'linux' in platform.system().lower():
        # Use your exact Linux logic
        ports_to_try = linux_ports
        print("Linux mode - using Pi UARTs")
    else:
        # Windows: Take first 4 available COM ports
        ports_to_try = available_ports[:4]
        print("Windows mode - using first 4 COM ports")

    uarts=[]
    for i, port in enumerate(ports_to_try):
        try:
            uart = serial.Serial(
                port, 
                baudrate=9600, 
                timeout=1
            )
            print(f"uart{i} opened: {port}")
            uarts.append(uart)
        except Exception as e:
            print(f"uart{i} failed {port}: {e}")
            uarts.append(None)  # Keep array length consistent
    
    return uarts
# if _RPpresent:
# # adjust to the actual device names you see in /dev
#     uart0 = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)
#     uart1 = serial.Serial("/dev/ttyAMA1", baudrate=9600, timeout=1)
#     uart2 = serial.Serial("/dev/ttyAMA2", baudrate=9600, timeout=1)
#     uart3 = serial.Serial("/dev/ttyAMA3", baudrate=9600, timeout=1)
#     #uart4 = serial.Serial("/dev/ttyAMA4", baudrate=9600, timeout=0.1)
#     uarts = [uart0, uart1, uart2, uart3]

# main
uart0, uart1, uart2, uart3 = get_uarts()
uarts = [uart0, uart1, uart2, uart3]
# end main


def UART_checkforLamps():
    for i in range(4):
        msg=SendUART(i+1, 'S:L:0')  #returns the msg
        #msg=uarts[i].readline()  # clear any existing data
        #ReadUART(i, msg.decode(errors="ignore"))
        #msgArr=msg.split(':')
        if msg==':::No Lamp found':
            
            if _debug:
                print('No response from Lamp', {i+1})   
            msg=':::No Lamp found'
            #ReadUART(i, msg)
            DisableFrame(i+1)
        else:
            EnableFrame(i+1)

        
                


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
    return ReadUART(lamp)

def ReadUART(lamp:int):
    msg=''
    msg=uarts[lamp-1].readline()  
    msg = msg.decode('utf-8', errors='ignore')
    msg=msg.rstrip('\r\n')
    if msg=='':
        msg=':::No Lamp found'
    if _postMsg:
        PostMsg(lamp,msg)
    
    msgArr=msg.split(':')
    if len(msgArr)==4:
        PostError(lamp, msgArr[3])
    if _debug:
        print ('Reading from UART:',msg)
    
    SetGet(lamp,msgArr)
    return msg
    
   
    
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
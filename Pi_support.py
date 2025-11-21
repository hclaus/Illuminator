
import sys
#import ScreenV1_support.py

_debug=True
_RPpresent=True

import serial

if _RPpresent:
# adjust to the actual device names you see in /dev
    uart0 = serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=0.1)
    uart1 = serial.Serial("/dev/ttyAMA1", baudrate=115200, timeout=0.1)
    uart2 = serial.Serial("/dev/ttyAMA2", baudrate=115200, timeout=0.1)
    uart3 = serial.Serial("/dev/ttyAMA3", baudrate=115200, timeout=0.1)
    uart4 = serial.Serial("/dev/ttyAMA4", baudrate=115200, timeout=0.1)

    uarts = [uart0, uart1, uart2, uart3, uart4]

def SetLamp(lamp,option):
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
    if lamp==1:
        UART='UART1'
    if lamp==2:
        UART='UART2'
    if lamp==3:
        UART='UART3'
    if lamp==4:
        UART='UART4'
    if _debug:
        print ('UART',{UART},'Text:',{txt})
   # uarts[lamp].write((txt+'\n').encode('utf-8'))
    sys.stdout.flush()
    
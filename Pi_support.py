import sys
#import ScreenV1_support.py

_debug=True
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
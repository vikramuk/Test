# -*- coding: utf-8 -*-
import time
import sys
import usb
import serial
import visa
#from HTMLReport import HTMLTestRunner

COMPORT =5
COMPORT=2 if (COMPORT ==0) else 5   # Check for COMPORT to other than Zero
BAUDRATE= 115200
OFFSET=5
DEVICE=1
DEVICE_RESET=1

#State logic for Relay
DEVICE_ERROR=0
RELAY_ERROR=0
APK_ERROR=0

'''
#TODO:  Check for the Device Name from FunctionGenerator.csv 
'''
AGILENT_33220A= "USB0::0x0957::0x0407::MY44021621::0::INSTR" # - for 33220A
AGILENT_33522A= "USB0::0x0957::0x2307::MY50003961::0::INSTR" # - for 33522A

def setUpCOMPort(channel,values):
    try:
        ser = serial.Serial((COMPORT-1),BAUDRATE, parity='N',bytesize=8, stopbits=1, timeout=None, xonxoff=False,rtscts=False, dsrdtr=False)  
        #print ser.name      # check which port was really used
        for value in range(60, int(values), 10):
            ser.write("US 1 1 1\n")
            print ("Sending Values to the US1 Channel")      
            time.sleep(5)
            print ("US 1 2 "+ str(value)+"\n")
            ser.write("US 1 2 "+ str(value)+"\n")            
            ser.close()           
        print("Disconnecting")
    #Fail Gracefully
    except IOError:
        print 'cannot Connect to Device COM: '+ str(COMPORT-1)+' PORT'        
    except Exception as e:
        print 'cannot Find the Device: '+ str(COMPORT-1)+' PORT'  
        ser.close()
    else:
        print "COM Port:" + str(COMPORT)+ " Connection has been Closed"

def test_List_Vendor():        
    dev = usb.core.find(find_all=True)
    # loop through devices, printing vendor and product ids in decimal and hex
    for cfg in dev:
        sys.stdout.write('Decimal VendorID=' + str(cfg.idVendor) +' & ProductID=' + str(cfg.idProduct) + '\n')
        sys.stdout.write('Hexadecimal: VendorID=' + hex(cfg.idVendor) + ' & ProductID=' + hex(cfg.idProduct) + '\n\n')    

def test_Values_USB():
    # Check for Device Availability
    try:
        rm = visa.ResourceManager()
        rm.list_resources()
        inst_33220A = rm.open_resource(AGILENT_33220A, read_termination="\r")
        inst_33220A.timeout = 25        
        print ("Checking Device Number: ")
        print(inst_33220A.query("*IDN?", delay=1))        
        print ("Checking Frequency Value")
        print(inst_33220A.query(":SOUR:FREQ?"))    
        print ("Checking Phase Value")    
        print(inst_33220A.query(":SOUR:BURS:PHAS?", delay=1))        
        print ("Checking Burst Value")    
        print(inst_33220A.write(":SOUR:BURS:NCYC?"))
        print(inst_33220A.read_raw())        
        print("Getting Values for Frequency")
        # print(inst_33220A.write_ascii_values(":SOUR1:FREQ:CW 1.1512 MHZ",termination=None, encoding=None))
        time.sleep(1)
        cw_freqy = float((inst_33220A.query(":SOUR1:FREQ?")))      
        print "Frequency is Set to:    ", cw_freqy # " Hertz"
        cw_amp = float(inst_33220A.query(':SOUR:VOLT:LEV:IMM:AMPL?'))
        print "Sample Rate:    ", cw_amp # " Volts"
        cw_bursttime = float(inst_33220A.query(":SOUR:BURS:NCYC?"))
        print "Burst Cycles:    ", cw_bursttime 
        output_impedance = float(inst_33220A.query(":OUTP1:LOAD?"))
        print "Output Impedance:    ", output_impedance # " Ohms"
        burst_phase = float(inst_33220A.query(":SOUR:BURS:PHAS?"))
        print "Burst Phase:    ", burst_phase  # " Degrees"
        burst_period = float(inst_33220A.query(":SOUR:BURS:INT:PER?"))
        print "Burst Period:    ", burst_period # " seconds"
        DEVICE_ERROR=1
    #Fail Gracefully
    except IOError:
        DEVICE_ERROR =0
        print 'cannot Connect to Device: '+ AGILENT_33220A
    except Exception as e:
        print 'cannot Find the Device: '+ AGILENT_33220A
    else:
        print "Connection to USB: Test has been Closed"

def set_Values_USB():
    # Check for Device Availability
    try:
        rm = visa.ResourceManager()
        rm.list_resources()
        inst_33220A = rm.open_resource(AGILENT_33220A, read_termination="\r")
        inst_33220A.timeout = 25        
        print ("Checking Device Number")
        print(inst_33220A.query("*IDN?", delay=1))
        # Disable Output
        print(inst_33220A.write(":OUTP1:STAT 0"))
        if (DEVICE_RESET):
            print(inst_33220A.write("*CLS"))          
        print(inst_33220A.write(":SOUR1:FREQ:CW 1.1512 MHZ"))
        print(inst_33220A.write(":SOUR1:VOLT:LEV:IMM:AMPL 0.1"))
        print(inst_33220A.write(":SOUR1:BURS:PHAS 0 DEG"))
        print(inst_33220A.write(":OUTP1:LOAD 50"))
        print(inst_33220A.write(":SOUR1:BURS:PHAS 0 DEG"))
        print(inst_33220A.write(":SOUR1:BURS:INT:PER 0.1 S"))
        # Enable Output
        print(inst_33220A.write(":OUTP1:STAT 1"))  
        DEVICE_ERROR=1      
    #Fail Gracefully
    except IOError:
        DEVICE_ERROR =0
        print 'cannot Connect to Device: '+ AGILENT_33220A
    except Exception as e:
        print 'cannot Find the Device: '+ AGILENT_33220A
    else:
        print "Connection to USB has been Closed"       

def launch_APK_AUT():
    start.application("com.ge.med.mic.lotus.squish")
    '''
    #TODO:   Check for Different APK
    ctx0 = startApplication("com.ge.med.mic.lotus.squish")
    setApplicationContext(ctx0)
    #"com.ge.med.mic.lotus.squish"  "com.ge.med.mic.lotus"
    '''
    waitForObject(":Monitoring Activity.Chart_Button")
    fhr = waitForObject(":Monitoring Activity.fhr_Text")
    test.verify(fhr,"FHR is Present")
    fhrVal = waitForObject(":Monitoring Activity.fhr_Text").text   #  fhr.text
    for i in range(0,4):
        test.verify(fhrVal > 49 and fhrVal < 51, "FHR value is between 49 and 51")        
    test.compare(fhrVal,"49") #waitForObject(":Monitoring Activity.fhr_Text").text, "139")        
    test.verify(fhrVal > 49 and fhrVal < 51, "FHR value is between 49 and 51")       
    '''    
    #TODO:   Debug the FHR values for US1
    {container=':Monitoring Activity_Activity' resourceName='fhr' text='Chart' type='Text' visible='true'}
    {container=':Monitoring Activity_Activity' resourceName='lib_navigation_chart_button' text='Chart' type='Button' visible='true'}
    '''
    '''
    doubleTap(waitForObject(":Monitoring Activity.lib_vsc_surface_view_View"), 258, 281)
    longPress(waitForObject(":Monitoring Activity.90_Text"), 40, 58)
    tapObject(waitForObject(":Monitoring Activity.content_Panel"), 372, 125)
    tapObject(waitForObject(":Monitoring Activity.Chart_Button"), 6, 46)
    doubleTap(waitForObject(":Monitoring Activity.lib_vsc_surface_view_View"), 418, 417)
    longPress(waitForObject(":Monitoring Activity.lib_vsc_surface_view_View"), 418, 432)
    '''
    # Checking Long Press in Object Map
    test.verify("AUT", "AUT")
    pass

def launch_FHR_AUT_COUNT(count):    
    if (DEVICE):        
        fhr = waitForObject(":Monitoring Activity.fhr_Text")        
        fhrVal = waitForObject(":Monitoring Activity.fhr_Text").text
        #:TODO:      Check the Expected and Actual Values from the CSV file FunctionGenerator.csv
        #source(findfile("Test Data", "FunctionGenerator.csv"))
        test.verify(fhrVal > float(count-OFFSET) and fhrVal < float(count+OFFSET), "FHR value is between 49 and 51")
    print str(float(count-OFFSET)) +", " +str(count) +", "+ str(float(count+OFFSET))       
    pass


def Set_Burst_Period(period):
# Check for Device Availability
    try:
        rm = visa.ResourceManager()
        rm.list_resources()
        inst_33220A = rm.open_resource(AGILENT_33220A, read_termination="\r")
        inst_33220A.timeout = 25
        period =float(period)# if (period == 0) else 0.1
        #(":SOUR1:BURS:INT:PER 0.5 S"))
        if (DEVICE):
            print ":SOUR1:BURS:INT:PER  "+ str(float(period))+ " S "        
        print (inst_33220A.write(":SOUR1:BURS:INT:PER "+ str(float(period))+ " S "))
        ch_burst_period = float(inst_33220A.query(":SOUR:BURS:INT:PER?"))
        print "Burst Period:    ", ch_burst_period # " seconds"
    #Fail Gracefully
    except IOError:
        DEVICE_ERROR =0
        print 'cannot Connect to Device: '+ AGILENT_33220A
    except Exception as e:
        print 'cannot Find the Device: '+ AGILENT_33220A
    else:
        print "Connection has been Closed"    

def main():
    #Check Device
    test_List_Vendor()
    #Set Values
    set_Values_USB()
    #Re-read the set values 
    test_Values_USB()
    #change the Burst period 
    Set_Burst_Period(0.1)
    #Launch the APK and connect to AUT
    #launch_APK_AUT()
    #change the Burst period 
    Set_Burst_Period(0.5) 
    #Change the Burst Period and wait for 2 Seconds tom check the Value
    if (DEVICE_ERROR and DEVICE):    # TODO: and the APK_ERROR and RELAY_ERROR states
        for i in range(1, 10):
            time.sleep(5)        
            Set_Burst_Period(i/10.0)
            if (DEVICE):   # TODO: and the APK_ERROR and RELAY_ERROR states
                launch_FHR_AUT_COUNT(i*10.0)     
                #Get Initial Values
                test_Values_USB() 
    #Sleep for Period
    time.sleep(3)    
    # TODO:  This Section is to Inject Values from the COM Port for the Various Channels
    if (DEVICE):     #Send Commands on COM Port    
        setUpCOMPort(COMPORT, 140)    
    
    
def init_Read_Config():
    Instruments={
                 "AGILENT_33522A":"USB0::0x0957::0x2307::MY50003961::0::INSTR", 
                 "AGILENT_33220A":"USB0::0x0957::0x0407::MY44021621::0::INSTR"
                }    
    FHRCount={0.5:120,
              0.6:100,
              0.7:85,
              0.8:74,
              0.9:66
             }
    print FHRCount.values()
    '''
    for row, record in enumerate(testData.dataset("FunctionGenerator.csv")):
        fields = testData.field(record, "Instrument"), testData.field(record, "CommandString")    
    for record in testData.dataset("FHR_Count.csv"):
        BurstPeriod = testData.field(record, "BurstPeriod")
        FHRValue = testData.field(record, "FHRValue")        
        test.log("%s %s " % (BurstPeriod, FHRValue, "\n"))
    '''

if __name__ == '__main__':    
    init_Read_Config()        
    main()
    
    
    

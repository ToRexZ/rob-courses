# -*- coding: utf-8 -*-
"""
Created on Wed Jun  1 10:58:47 2016

@author: Gaurakumar Patel

Comments:

This code can send Square/Triangular waves to the Prosthesis
It can Revieve the data back from sensors/EMG

Please Get the Michelangelo Communication Interface from Marko
Go to ../MichaelAngeloHand/DLLs and click on the application "MichelangeloGUI" (the .exe file)

DONGLE: Connect the Bluetooth Dongel to the Computer, and in the GUI choose which Dongel has
been connected either "Slow" or "Fast"

DUMP MODE: The default dump mode is "(100Hz) EMG + Sensors", this will give you data at 100 Hz,
this data will have EMG values from the EMG electrodes and Sensor Values. Five sensor values will
be provided: Grip Type, Force, Aperture, Wrist Pronation/Supination and Wrist Flexion/Extension

Turn-ON the HAND: press the button (on the hand) for a long time until you here two short beeps twice.
So the sound that will come out will be like "...beep,beep,......,beep,beep..." (so, in total 4 beeps).
If you here only the fist two beep like: "...beep,beep,..." then the BLUETOOTH is not active. After
you here the first two beeps you need to wait for the next two.

To CONNECT: to connect, press the "Connect" button. It may take some time, wait till the button text
changes to disconnect.

CALIBRATION: in the calibration group, click on the "load .xml file", depedning on what hand you have,
choose your .xml file.

COMMUNICATION: To begin RECEIVING of commands from your code click on the "Start Communiction" command.
To send the EMG+Sensor data over the UPD, click on the "Start Dump" button

Then use this code or your own code to communicate-with/control the Michealangelo Hand.

"""

##Libraries need for Python
import pylab
from pylab import *
import matplotlib.pyplot as plt
import socket
import numpy
from time import time

########################################################
## TRANSMITTER and RECIEVER
########################################################

LocalIP = "127.0.0.1"   #This is the local IP of your Computer
REC_PORT = 8052         #The INTERFACE sends data to this Port
TRNS_PORT = 8051        #The INTERFACE will recieve COMMANDs at this Port

#We create a SOCKET for transmission
transSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#We create a SOCKET for Receiving
recSock = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
try:
    recSock.bind( ( LocalIP, REC_PORT ) )
except:
    print('Error Occured during binding the RECIEVER')



########################################################
## WAVE GENERATOR
########################################################
# You can create Square or Triangular waves with this function
#These waves can be sent a "commands" to the prosthesis
#This function is just for Demo, no need to understand it to control the Prosthesis

def getWave (RiseEdge, Plateau, PhaseShift, Rate, Seperation, Levels):

    tDuration = RiseEdge #seconds Rise time
    tPlateau = Plateau #seconds
    tPhase = PhaseShift #seconds
    tRate = Rate #Hz
    tSeperationInterval = Seperation #seconds
    tWaveLevels = Levels
    tSamples = ((2 * tDuration + tPlateau + tSeperationInterval) * len(tWaveLevels) + tPhase)  * tRate
    tWave = [0] * int(tPhase * tRate)

    for lev in range(len(tWaveLevels)):
        for s in range(int(tDuration * tRate)):
            tWave.append(tWaveLevels[lev] * (s/tRate))
        for s in range(int(tPlateau * tRate)):
            tWave.append(tWaveLevels[lev])
        for s in range(int(tDuration * tRate)):
            tWave.append(tWaveLevels[lev] * (1 - s/tRate))
        for s in range(int(tSeperationInterval * tRate)):
            tWave.append(0)

    return numpy.array(tWave)

##########################################################
##RECIEVE & TRANSMIT DATA MHand
##########################################################


########################################################
##The Formate for all the values to be Transmitted:#####
########################################################
##1. "Velocity MODE": it has 9 unsigned-bytes###########
##byte0 = 1: to indicate velocity mode
##byte1 = Palmar Grip Closing command in range [0, 255]
##byte2 = Palmar Grip Opening command in range [0, 255]
##byte3 = Lateral Grip Closing command in range [0, 255]
##byte4 = Lateral Grip Opening command in range [0, 255]
##byte5 = Pronation Velocity in range [0, 255]
##byte6 = Supination Velocity in range [0, 255]
##byte7 = Flexion Velocity in range [0, 255]
##byte8 = Extension Velocity in range [0, 255]
#######################################################
##2. "Position Control Mode": it has 5 signed-bytes####
##signed_byte0 = 2: to indicate velocity mode
##signed_byte1 = Grip Type, 0 - Palmar, 1 - Lateral
##signed_byte2 = Grip Closure in range [0, 100]
##signed_byte3 = Supination/Pronation in range [-100, 100]; where, Pronation is done with a Positive Command
##signed_byte4 = Extension/Flexion in range [-100, 100]; where, Flexion is done with a Negative Command



TR_PacketLEN = 9 #We will send VELOCITY commands, the length thus is 9 unsigned-bytes
#****If you want to change to Postion mode, change the packet size to 5, simply uncomment the following line,
#TR_PacketLEN = 5

StoreLen = 6
StoredSignal = numpy.zeros((1,StoreLen))

##We will send a Square-Wave it a duration of 2 seconds to the hand stored in the variable "HandCommand"
##You can visualize the plot of the hand Command in Figure 1

HandCommand1 = getWave(0, 2, 0, 100, 5, [0.2, 0.5, 1])
HandCommand2 = getWave(0, 2, 3, 100, 5, [0.2, 0.5, 1])
if(TR_PacketLEN == 5):
    HandCommand1 = getWave(0, 5, 0, 100, 0, [0.2, 0.5, 1])
    HandCommand2 = getWave(0, 5, 5, 100, 0, [0.2, 0.5, 1])

plt.figure(1)
plt.plot(HandCommand1)
plt.plot(HandCommand2)
plt.show()

##Reference time Stamp, not Important for Control of Hand
startTime = time()

for c in range(len(HandCommand1)):

    #############################################################
    ##RECIEVE DATA
    #############################################################
    try:
        data = recSock.recv(1024) #Recieve Message from the GUI
    except:
        print("Reciever Error")

    tempBuf = numpy.zeros((1,StoreLen))
    tempBuf[0,0] = time()-startTime ##TIME STAMP

    for j in range(5): ##STORING the REC_DATA into a temporary buffer
        tempBuf[0,1+j] = int.from_bytes(data[j+5:j+6], byteorder='big', signed=True) ##Convert Message from BYTES to INT

    ###############################################################
    ## SEND DATA
    ###############################################################

    if(TR_PacketLEN == 9):   #VELOCITY MODE
        ControlSignal = numpy.zeros((1,TR_PacketLEN))  #This signal will be sent over the UDP Port, it has 9 values
        ControlSignal[0,0] = 1 #We put byte0 = 1, to indicate VELOCITY MODE
        ControlSignal[0,1] = HandCommand1[c] ## we will send the SQUARE wave to make PALMAR CLOSING in the hand, hence byte1 is set
        ControlSignal[0,2] = HandCommand2[c] ## we will send the SQUARE wave to make PALMAR OPENING in the hand, hence byte2 is set

        ##the above Variables are "doubles", now we need to convert them to "unsigned-bytes"
        MESSAGE = int(ControlSignal[0,0]).to_bytes(1,byteorder='big',signed=True)   ##Contains the Final data as "Unsigned BYTES"
        for j in range(1,TR_PacketLEN):
            MESSAGE = MESSAGE + int(ControlSignal[0,j]*254).to_bytes(1, byteorder='big')

        transSock.sendto(MESSAGE, (LocalIP, TRNS_PORT)) #MESSAGE sent over the UDP

    elif(TR_PacketLEN == 5):
        ControlSignal = numpy.zeros((1,TR_PacketLEN))  #This signal will be sent over the UDP Port, it has 9 values
        ControlSignal[0,0] = 2 #We put byte0 = 1, to indicate VELOCITY MODE
        ControlSignal[0,1] = 1 #The LATERAL Grasp
        ControlSignal[0,2] = HandCommand1[c] ## we will send the SQUARE wave to change aperture of lateral Grasp
        ControlSignal[0,3] = HandCommand2[c] ## we will send the SQUARE wave to change the wrist rotation

        ##the above Variables are "doubles", now we need to convert them to "unsigned-bytes"
        MESSAGE = int(ControlSignal[0,0]).to_bytes(1,byteorder='big',signed=True)   ##Contains the Final data as "Unsigned BYTES"
        MESSAGE = MESSAGE + int(ControlSignal[0,1]).to_bytes(1,byteorder='big',signed=True)
        for j in range(2,TR_PacketLEN):
            MESSAGE = MESSAGE + int(ControlSignal[0,j]*100).to_bytes(1, byteorder='big',signed=True)
        print(MESSAGE)
        transSock.sendto(MESSAGE, (LocalIP, TRNS_PORT)) #MESSAGE sent over the UDP

    ################################################################
    ##STORE DATA
    ################################################################
    StoredSignal = numpy.concatenate((StoredSignal,tempBuf),axis=0)


plt.figure(2)
plt.plot(StoredSignal[:,0], StoredSignal[:,2:StoreLen-1]) ##The Plot of the Sensor Data: Aperture, Rotation, Flexion and Force vs. Time
plt.show()

























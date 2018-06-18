import serial
import time

def openUArm(uArmPort):
    '''Open the uArm serial port
    Typically port is /dev/ttyACM0'''
    
    uArm = serial.Serial(uArmPort,115200, timeout=2)
    time.sleep(2)  #pause for a bit

    #listen to the port for the uArm boot-up sequence, and print it
    print(wait4Response(uArm,10))
    time.sleep(2)  #pause for a bit
    print(getResponse(uArm))
    return uArm

def wait4Response(ser, timeOut):
    """ Waits for a 'line' response from the serial port
        Returns the string response
        If no response after timeOut, returns and empty string
    """
    startTime = time.time()
    Response = ""
    while Response == "" and time.time()- startTime < timeOut:
        if ser.inWaiting() > 0:
            #time.sleep(1)
            Response = ser.readline().decode("utf-8")
    return Response

def getResponse(ser):
    """ Returns any data from the serial input buffer
        No waiting, no timeout
    """
    serData=""
    while ser.inWaiting()>0:
        serData =  serData + ser.read(1).decode("utf-8")
    return serData


#==============================================================
#   NEW FUNCTION - this works pretty well. Shouldn't need fixing
#==============================================================

def sendGCode(uArm, gCode):
    '''Sends some g-code to the robot and waits for the robot to respond
    To make this really good, it would be good to check if the robot says "OK" or whether there
    is an error, and return either "TRUE" or an error number'''
    
    print("Sending: " + gCode)
    uArm.write(("\r" + gCode + "\r").encode("utf-8"))
    print("Received: ", wait4Response(uArm, 20))   #wait for response
    print(getResponse(uArm))                       #soak up any extra chars

def goHome(uArm):
    '''Puts the uArm into the home position'''
    sendGCode(uArm, "G0 X150 Y0 Z0 F20000")    #pen up (if not already up)
    
def drawBoard(uArm):
    '''Draws the board'''
    sendGCode(uArm, "G0 X150 Y0 Z10")  
    sendGCode(uArm, "G0 X150 Y25 Z10")
    sendGCode(uArm, "G0 X150 Y25 Z0")
    sendGCode(uArm, "G0 X225 Y25 Z0")
    sendGCode(uArm, "G0 X225 Y25 Z10")
    sendGCode(uArm, "G0 X200 Y0 Z10")
    sendGCode(uArm, "G0 X200 Y0 Z0")
    sendGCode(uArm, "G0 X200 Y75 Z0")
    sendGCode(uArm, "G0 X200 Y075 Z10")
    sendGCode(uArm, "G0 X225 Y50 Z10")
    sendGCode(uArm, "G0 X225 Y50 Z0")
    sendGCode(uArm, "G0 X150 Y50 Z0")
    sendGCode(uArm, "G0 X150 Y50 Z10")
    sendGCode(uArm, "G0 X175 Y75 Z10")  
    sendGCode(uArm, "G0 X175 Y75 Z0")
    sendGCode(uArm, "G0 X175 Y0 Z0")
    sendGCode(uArm, "G0 X175 Y0 Z10")
    sendGCode(uArm, "G0 X150 Y0 Z10")
    sendGCode(uArm, "G0 X150 Y0 Z10")
    
def drawNought(uArm, whichSquare):
    '''Draws a nought at the position on the board specified by "whichSquare")
    eg: drawNought(1) draws a nought in square 1
        drawNought(2) draws a nought in square 2
    squares are as follows:
      0|1|2
      -----
      3|4|5
      -----
      6|7|8    '''

    #work out starting position based on which square:
    if whichSquare == 0:
        x=150
        y=0
    elif whichSquare == 1:
        x=150
        y=25
    elif whichSquare == 2:
        x=150
        y=50
    elif whichSquare == 3:
        x=175
        y=0
    elif whichSquare == 4:
        x=175
        y=25
    elif whichSquare == 5:
        x=175
        y=50
    elif whichSquare == 6:
        x=200
        y=0
    elif whichSquare == 7:
        x=200
        y=25
    elif whichSquare == 8:
        x=200
        y=50


    sendGCode(uArm, "G0 Z50")    #pen up (if not already up)
    sendGCode(uArm, "G0 X" + str(x) + " Y"+ str(y))   #got to the starting location
    
    sendGCode(uArm, "G91")       #switch to relative move mode
    sendGCode(uArm, "G0 X5 Y10")
    
    sendGCode(uArm, "G90")       #switch back to absolute mode
    sendGCode(uArm, "G0 Z0")     #pen down
    sendGCode(uArm, "G91")       #switch to relative move mode

    #draw the nought
    sendGCode(uArm, "G0 Y5")
    sendGCode(uArm, "G0 X5 Y5")
    sendGCode(uArm, "G0 X5 ")
    sendGCode(uArm, "G0 X5 Y-5")
    sendGCode(uArm, "G0 Y-5")    
    sendGCode(uArm, "G0 X-5 Y-5")
    sendGCode(uArm, "G0 X-5")
    sendGCode(uArm, "G0 X-5 Y5")

    sendGCode(uArm, "G90")       #switch back to absolute mode
    sendGCode(uArm, "G0 Z50")    #pen up

def drawCross(uArm, whichSquare):
    '''Draws a cross at the position on the board specified by "whichSquare")
    eg: drawCross(1) draws a nought in square 1
        drawCross(2) draws a nought in square 2
    squares are as follows:
      0|1|2
      -----
      3|4|5
      -----
      6|7|8    '''

    #work out starting position based on which square:
    #(These are wrong... needs work!)
    if whichSquare == 0:
        x=150
        y=0
    elif whichSquare == 1:
        x=150
        y=25
    elif whichSquare == 2:
        x=150
        y=50
    elif whichSquare == 3:
        x=175
        y=0
    elif whichSquare == 4:
        x=175
        y=25
    elif whichSquare == 5:
        x=175
        y=50
    elif whichSquare == 6:
        x=200
        y=0
    elif whichSquare == 7:
        x=200
        y=25
    elif whichSquare == 8:
        x=200
        y=50


    sendGCode(uArm, "G0 Z50")    #pen up (if not already up)
    sendGCode(uArm, "G0 X" + str(x) + " Y"+ str(y))   #go to the starting location
    
    sendGCode(uArm, "G91")       #switch to relative move mode
    sendGCode(uArm, "G0 X5 Y5")
    
    sendGCode(uArm, "G90")       #switch back to absolute mode
    sendGCode(uArm, "G0 Z0")     #pen down
    sendGCode(uArm, "G91")       #switch to relative move mode

    #draw the cross
    sendGCode(uArm, "G0 X15 Y15")
    sendGCode(uArm, "G0 Z20")     #pen up
    sendGCode(uArm, "G0 X-15")
    sendGCode(uArm, "G0 Z-20")    #pen down
    sendGCode(uArm, "G0 X15 Y-15")
    sendGCode(uArm, "G0 Z0")

    sendGCode(uArm, "G90")       #switch back to absolute mode
    sendGCode(uArm, "G0 Z50")    #pen up

def drawWinLine(uArm, winLine):
    '''Draws a line through the winning positions
       Parameters: uArm - the robot arm to do the drawing
                   winLine - a string representing the positions to draw through
                   eg: "012" or "248" or "147"
    '''
    
    sendGCode(uArm, "G0 Z50")    #pen up (if not already up)
    
    if winLine == "012":
        #put some code to draw a line through "012"
        sendGCode(uArm, "G0 X162.5 Y0")
        sendGCode(uArm, "G0 Z0")
        sendGCode(uArm, "G0 X162.5 Y75")
        
    elif winLine == "258":
        #puts some code to draw a line through "345"  
        sendGCode(uArm, "G0 X150 Y62.5")
        sendGCode(uArm, "G0 Z0")
        sendGCode(uArm, "G0 X225 Y62.5")
        
    elif winLine == "345":
        #puts some code to draw a line through "345"  
        sendGCode(uArm, "G0 X187.5 Y0")
        sendGCode(uArm, "G0 Z0")
        sendGCode(uArm, "G0 X187.5 Y75")
        
    elif winLine == "678":
        #puts some code to draw a line through "345"  
        sendGCode(uArm, "G0 X212.5 Y0")
        sendGCode(uArm, "G0 Z0")
        sendGCode(uArm, "G0 X212.5 Y75")
        
    elif winLine == "147":
        #puts some code to draw a line through "345"  
        sendGCode(uArm, "G0 X150 Y37.5")
        sendGCode(uArm, "G0 Z0")
        sendGCode(uArm, "G0 X225 Y37.5")
        
    elif winLine == "036":
        #puts some code to draw a line through "345"  
        sendGCode(uArm, "G0 X150 Y12.5")
        sendGCode(uArm, "G0 Z0")
        sendGCode(uArm, "G0 X225 Y12.5")
        
    elif winLine == "246":
        #puts some code to draw a line through "345"  
        sendGCode(uArm, "G0 X150 Y75")
        sendGCode(uArm, "G0 Z0")
        sendGCode(uArm, "G0 X225 Y0")
        
    elif winLine == "048":
        #puts some code to draw a line through "345"  
        sendGCode(uArm, "G0 X150 Y0")
        sendGCode(uArm, "G0 Z0")
        sendGCode(uArm, "G0 X225 Y75")
        
    
    #need code for the following winLines:  012, 345, 678, 036, 147, 258, 048, 246
    
    sendGCode(uArm, "G0 Z50")    #pen up
        


#
#   Noughts and Crosses Game
#   ========================
#
#   Ian Thompson 2018
#   0414270210  ianmelandkids@gmail.com
#   
#   Plays noughts and crosses using a simple machine learning algorithm.
#   
#   The computer starts out completely "dumb"; it plays by the rules but has
#   no clue how to win or lose. (except it can regonise a 'next move win' opportunity).
#
#   But over time, it builds up two "experience" lists, which are essentially
#   lists of "boards" (simplified so equivalent boards are combined), with votes
#   saying whether that board is a good board (led to a win) or a bad board
#   (led to a loss), and makes decisions using that experience.
#
#   After a dozen or so games, it starts to play reasonably smart, and eventually 
#   becomes quite difficult, if not impossible to defeat.
#
#   The board is represented by a string of exactly nine characters.
#   Each character represents a particular position on the board:
#
#       0|1|2
#       -----
#       3|4|5
#       -----
#       6|7|8
#
#   Each character can be "X" or "O" or " " (unoccupied)
#   So the board:
#   
#       X|X|O
#       -----
#       X| |O
#       -----
#       O|X|
#
#   Would be written as: "XXOX OOX " 

import random       #for choosing random moves
import collections  #gamelist needs to be an ordered dictionary
import uArmFunctions     #library of functions to control uArm
import computerVisionFunctions

import cv2             #opencv library
import numpy as np     #opencv library support
import time            #for time delays

"""%%%%%%%%%%%%% NORMAL ROBOT ARM AND GAME FUNCTIONS %%%%%%%%%%%%%%"""

def drawGrid():
    uArmFunctions.goHome(uArm)
    input("Clean board for new game. Press ENTER when ready")
    print("Drawing Board")
    uArmFunctions.drawBoard(uArm)
            
def drawLastMove(brd):
    
    global lastDrawnBoard
    global uArm
    global computerGoesFirst

    #draw any moves that haven't yet been drawn
    for i in range(0,9):
        if brd[i] != lastDrawnBoard[i]:
            print("Drawing", brd[i], "in position", i)
            if brd[i] == 'O':
                if computerGoesFirst:
                    #0 will be drawn by the human
                    pass
                else:
                    uArmFunctions.drawNought(uArm, i)
            if brd[i] == 'X':
                if computerGoesFirst:
                    uArmFunctions.drawCross(uArm, i)
                else:
                    #X will be drawn by the human
                    pass

    #update the record of what has already been drawn
    lastDrawnBoard = brd

def printBrd(brd):
    """ Outputs the board represented by 'brd' to the screen"""
    print(brd[0],"|",brd[1],"|",brd[2], sep="")
    print("-----")
    print(brd[3],"|",brd[4],"|",brd[5], sep="")
    print("-----")
    print(brd[6],"|",brd[7],"|",brd[8], sep="")

def humanMoveVision(brd, video, board_lines):
    """ Gets the human's next move using the screen and keyboard """
    #determine which player is moving (X always moves first)
    if brd.count("O") == brd.count("X"):
        player="X"
    else:
        player="O"

    newBrd=""
    validMove=False
    while not validMove:                                                #keep looping until valid move
        print("You are ", player, end=". ")
        #play the game
        #refresh the video stream
        computerVisionFunctions.refreshWebcam(video)
        
        _, original_image = video.read()
        while True:
            move_played, row, col = computerVisionFunctions.checkPlayerMove(video, board_lines, original_image)
            if move_played:
                break
            else:
                print("You did not make a move, please make a move")
        
        #map rows and columns to 'move'
        if row == 1 and col == 1:
            move = 8
        elif row == 1 and col == 2:
            move = 7
        elif row == 1 and col == 3:
            move = 6
        elif row == 2 and col == 1:
            move = 5
        elif row == 2 and col == 2:
            move = 4
        elif row == 2 and col == 3:
            move = 3
        elif row == 3 and col == 1:
            move = 2
        elif row == 3 and col == 2:
            move = 1
        elif row == 3 and col == 3:
            move = 0
        
        print("Your move was " + str(move) + ".")
        
        try:                                                            #try converting to an int
            #move=int(strMove[0])
            if move<0 or move>8 or brd[move] != " ":                    #move in correct range and not a square already taken?
                print("Invalid move - enter a move between 0 and 8:")
                printBrd("012345678")
                print("")
                printBrd(brd)
            else:
                validMove=True
                for i in range(0,9):                                    #if valid int, add the move to the board
                    if i == move:
                        newBrd=newBrd + player
                    else:
                        newBrd = newBrd + brd[i]
        except:                                                         #do this if the input wasn't an int
            #if strMove=='x':
            #    printExperience()
            #elif strMove=="load":
            #    loadExperience()
            #else:
            print("Invalid move - enter a move between 0 and 8:")
            printBrd("012345678")
            print("")
            printBrd(brd)
    return newBrd

def humanMove(brd):
    """ Gets the human's next move using the screen and keyboard """
    #determine which player is moving (X always moves first)
    if brd.count("O") == brd.count("X"):
        player="X"
    else:
        player="O"

    newBrd=""
    validMove=False
    while not validMove:                                                #keep looping until valid move
        print("You are ", player, end=". ")
        strMove = input("What is your move? (0-8): ")
        try:                                                            #try converting to an int
            move=int(strMove[0])
            if move<0 or move>8 or brd[move] != " ":                    #move in correct range and not a square already taken?
                print("Invalid move - enter a move between 0 and 8:")
                printBrd("012345678")
                print("")
                printBrd(brd)
            else:
                validMove=True
                for i in range(0,9):                                    #if valid int, add the move to the board
                    if i == move:
                        newBrd=newBrd + player
                    else:
                        newBrd = newBrd + brd[i]
        except:                                                         #do this if the input wasn't an int
            if strMove=='x':
                printExperience()
            elif strMove=="load":
                loadExperience()
            else:
                print("Invalid move - enter a move between 0 and 8:")
                printBrd("012345678")
                print("")
                printBrd(brd)
    return newBrd

def altIsGameWon(brd):
    
    global winLine
    
    for player in "OX":
        if brd[0]==player and brd[1]==player and brd[2]==player:
            winLine = "012"
            return player
        if brd[3]==player and brd[4]==player and brd[5]==player:
            winLine = "345"
            return player
        if brd[6]==player and brd[7]==player and brd[8]==player:
            winLine = "678"
            return player
        if brd[0]==player and brd[3]==player and brd[6]==player:
            winLine = "036"
            return player
        if brd[1]==player and brd[4]==player and brd[7]==player:
            winLine = "147"
            return player
        if brd[2]==player and brd[5]==player and brd[8]==player:
            winLine = "258"
            return player
        if brd[0]==player and brd[4]==player and brd[8]==player:
            winLine = "048"
            return player
        if brd[2]==player and brd[4]==player and brd[6]==player:
            winLine = "246"
            return player

    #no winner, so check for a draw (board has no empty spaces)
    if brd[:9].count(" ")==0:
        return "D"

    #If there's no winner, and no draw, the game is still underway:
    return "N"



def isGameWon(brd):
    """ Check to see if the game has been won:
        Returns winner: 'X', 'O' or 'D' (Draw) or 'N' (no result yet)
        Rotates a copy of the board 3 times looking for: three on the top row, three on the middle row, three diagonal
    """
    #look for a winning combination by either X or O by checking for 3 patterns, with various rotations
    for r in range(0,4):
        for i in "OX":
            if brd[0]==i and brd[1]==i and brd[2]==i:
                return i
            elif brd[0]==i and brd[4]==i and brd[8]==i:
                return i
            elif brd[3]==i and brd[4]==i and brd[5]==i:
                return i
        brd=tfRotate(brd)
    
    #no winner, so check for a draw (board has no empty spaces)
    if brd[:9].count(" ")==0:
        return "D"

    #If there's no winner, and no draw, the game is still underway:
    return "N"

def nextMoves(brd):
    """ Creates a list of all possible next moves
        Assumes "X" always goes first when determining whose turn it is
    """
    if brd.count("O") == brd.count("X"):
        player="X"
    else:
        player="O"

    nextMoveList=[]
    for i in range(0,9):
        if brd[i]==" ":
            newBrd=""
            for j in range(0,9):
                if j == i:
                    newBrd=newBrd + player
                else:
                    newBrd = newBrd + brd[j]
            nextMoveList.append(newBrd)
    return nextMoveList

def tfRotate(brd):
    """ Returns a string representing the board rotated once clockwise """
    newBrd=brd[6] + brd[3] + brd[0] + brd[7] + brd[4] + brd[1] + brd[8]+ brd[5] + brd[2]
    return newBrd

def tfUnrotate(brd):
    """ Returns a string representing the board rotated once anti-clockwise """
    newBrd=brd[2] + brd[5] + brd[8] + brd[1] + brd[4] + brd[7] + brd[0]+ brd[3] + brd[6]
    return newBrd

def tfFlip(brd):
    """ Returns a string representing the board flipped (refelcted) about the diagonal"""
    newBrd=brd[0] + brd[3] + brd[6] + brd[1] + brd[4] + brd[7] + brd[2]+ brd[5] + brd[8]
    return newBrd

def tfToggle(brd):
    """ Returns a string representing the board with O and X toggled"""
    newBrd=""
    for digit in brd:
        if digit == 'X':
            newBrd=newBrd + "O"
        elif digit == 'O':
            newBrd=newBrd + "X"
        else:
            newBrd=newBrd + " "
    return newBrd

def tfInt(brd):
    """Returns the board as an int with
        empty = 0
            O = 1
            X = 2
    """
    newBrd=""
    for digit in brd:
        if digit == 'X':
            newBrd=newBrd + "2"
        elif digit == 'O':
            newBrd=newBrd + "1"
        else:
            newBrd=newBrd + " "
    return newBrd

def rootBoard(brd):
    """ Returns a string representing a unique 'root' board for the given board.
        This is because many different board positions are logically identical, just rotated or flipped
        versions of a different board. This version matches those logically idential boards.
    """
    rootScore=0     #the "score" of the highest scoring board
    seqCount=0      #track the number of transforms so far
    tfBrd=brd       #the board after the latest transform

    tfSequence="rrrrfrrrr"
    
    #execute the next transform in the sequence
    for tf in list(tfSequence):
        if tf=="r":
            tfBrd=tfRotate(tfBrd)
        elif tf=="f":
            tfBrd=tfFlip(tfBrd)

        #score the transformed board by converting it into an integer
        Score = int(tfBrd.replace("X","2").replace("O","1").replace(" ","0"))
        #remember the best scoring board AND the number of transforms required to get to it
        if Score > rootScore:
            rootScore = Score
            rootBrd = tfBrd
    return rootBrd

def findBestMove(brd):
    maxVotes=0
    bestMove=random.choice(nextMoves(board))
    
    if brd.count("O")<brd.count("X"):                           #if it's O's move
        for m in nextMoves(brd):
            if isGameWon(m)=="O":                                    #if the move results in a win, just take it!
                return m
            if rootBoard(m) in O_Experience:                    #otherwise look for the best move in the experience list
                if O_Experience[rootBoard(m)] > maxVotes:
                    bestMove=m
                    maxVotes = O_Experience[rootBoard(m)]
        return bestMove

    if brd.count("X")==brd.count("O"):                          #if it's X's move
        for m in nextMoves(brd):
            if isGameWon(m)=="X":                                    #if the move results in a win, just take it!
                return m
            if rootBoard(m) in X_Experience:                    #otherwise look for the best move in the experience list
                if X_Experience[rootBoard(m)] > maxVotes:
                    bestMove=m
                    maxVotes = X_Experience[rootBoard(m)]
        return bestMove



def learnFromGame(Game):
    """ Remembers the moves that lead to a win in the Xexperience or Oexperience dictionaries
    """
    global X_Experience     #use the global experience list for the X player
    global O_Experience     #use the global experience list for the O player
    
    lastBrd = next(reversed(Game))                      #get the last board in the Game to check the result
    Winner = isGameWon(lastBrd)

    if Winner == "X":
        for g in Game:
            if g.count("X")>g.count("O"):               #every move of X's was good!
                if g in X_Experience:
                    X_Experience[g]=X_Experience[g]+2   #if the move is known, increment vote by 2
                else:
                    X_Experience[g]=2                   #else add it into the experience with vote=2
          
            else:                                       #every move of O's was bad!
                if g in O_Experience:
                    O_Experience[g]=O_Experience[g]-2   #if the move is known, decrement vote by 2
                else:
                    O_Experience[g]=-2                  #else add it into the experience with vote=-2

    if Winner == "O":
        for g in Game:
            if g.count("O")==g.count("X"):               #every move of O's was good!
                if g in O_Experience:
                    O_Experience[g]=O_Experience[g]+2   #if the move is known, increment vote by 2
                else:
                    O_Experience[g]=2                   #else add it into the experience with vote=2
            
            else:                                       #every move of X's was bad!
                if g in X_Experience:
                    X_Experience[g]=X_Experience[g]-2   #if the move is known, decrement vote
                else:
                    X_Experience[g]=-2                  #else add it into the experience with vote=-2


    if Winner == "D":                                   #If the game was a draw, that's better than 'unknown', so
        for g in Game:
            if g.count("X")>g.count("O"):               #every move of X's was not great, but 'ok'!
                if g not in X_Experience:
                    X_Experience[g]=1                   #add it into the experience with vote=1

            else:                                       #every move of O's was also not great, but 'ok'!
                if g in O_Experience:
                    O_Experience[g]=1                   #else add it into the experience with vote=1

def printExperience():

    #Print out X_Experience, showing votes
    print("X Experience:")
    for x in X_Experience:
        print(x," : ",X_Experience[x])

    #Print out O_Experience, showing votes
    print("O Experience:")
    for x in O_Experience:
        print(x," : ",O_Experience[x])
    print("")

def saveExperience():
    '''Saves the experience dictionary into a file called 'experience.txt'''

    print("Saving Experience:")

    expFile = open("experience.txt", "w")
    
    expFile.write("Game Count=" + str(gameCount) + "\n")
        
    expFile.write("Experience for X:\n")
    for x in X_Experience:
        expFile.write(x + " : " + str(X_Experience[x]) + "\n")

    expFile.write("Experience for O:\n")
    for o in O_Experience:
        expFile.write(o + " : " + str(O_Experience[o]) + "\n")

    expFile.close()

def loadExperience():
    '''Loads the experience from the file "experience.txt into the X_Experience and O_Experience'''
    global X_Experience
    global O_Experience
    global gameCount

    X_Experience={}             #This is the list of boards after X's move with votes showing how good each board situation is
    O_Experience={}             #This is the list of boards after O's move with votes showing how good each board situation is
    gameCount=0                 #How many games have been played? (how experienced is the computer?)
    loading=""

    try:
        with open("experience.txt", "r") as expFile:
            fileLines=expFile.readlines()
        for line in fileLines:
            if line[:11] == "Game Count=":
                gameCount=int(line[11:])
                print("loading experience from", int(line[11:]), "games...")
            elif line[:16] == "Experience for X":
                loading="X"
            elif line[:16] == "Experience for O":
                loading="O"
            elif line[10:11]==":":
                brd,score = line.split(":")
                if loading=="X":
                    X_Experience[brd[:9]]=int(score)
                elif loading=="O":
                    O_Experience[brd[:9]]=int(score)
    except IOError:
        print("No experience file found")

# ========================
# MAIN PROGRAM STARTS HERE
# ========================

#Global Variables
X_Experience={}             #This is the list of boards after X's move with votes showing how good each board situation is
O_Experience={}             #This is the list of boards after O's move with votes showing how good each board situation is
gameCount=0                 #How many games have been played? (how experienced is the computer?)
computerGoesFirst=False     #who will go first next game?
computersTurn=False         #keeps track of who's turn it is during a game
lastDrawnBoard="         "  #This keeps track of which Os and Xs have already been drawn, so the program knows what to draw
winLine="000"               #the line to draw after a won game

loadExperience()            #if an experience file called 'experience.txt' exists in the program directory, load it!
uArm=uArmFunctions.openUArm('/dev/ttyACM0')

#begin video capture
video = cv2.VideoCapture(0)

#play games over and over
while True:

    #Initialise the game
    board="         "
    GameList=collections.OrderedDict()
    printBrd("012345678") 
    drawGrid()                              #get the robot arm to draw the grid
    #identify the drawn board using computer vision
    #reposition the camera to check the board
    uArmFunctions.goVision(uArm)
    #refresh the video stream
    computerVisionFunctions.refreshWebcam(video)
    #check the gameboard
    _, frame = video.read()
    time.sleep(2) #give the robot arm time to stabilize camera
    cv2.imshow("Robot thinking", frame)
    cv2.waitKey(50) #this time delay gives python time to show the image
    is_gameboard, board_lines = computerVisionFunctions.detect_gameboard(frame)
    if is_gameboard == False:
        print("Gameboard could not be detected by camera. Trying gameboard detection again.")
        _, frame = video.read()
        time.sleep(2) #give the robot arm time to stabilize
        cv2.imshow("Robot thinking", frame)
        cv2.waitKey(50) #this time delay gives python time to show the image
        is_gameboard, board_lines = computerVisionFunctions.detect_gameboard(frame)
        if is_gameboard == False:
            print("Gameboard could not be detected by camera. Exiting program.")
            break
    
    lastDrawnBoard="         "              #the last drawn board was blank
    computersTurn=computerGoesFirst         #who's turn is it to go first?
        
    if computersTurn:
        print("\nStep aside human, I'm going first!")
    else:
        print("\nYou can go first")

    #this is the main gaim loop. Break from the loop with the game if NOT "No result yet (N)" ie: when there is a result
    while True:
        
        if computersTurn:
            board=findBestMove(board)       #find the best move (based on experience)
            printBrd(board)                 #display the move
            computersTurn=False             #computers turn is over
            
        else:
            #board=humanMove(board)          #get the human's move
            #reposition the camera to check the board
            uArmFunctions.goVision(uArm)
            time.sleep(2)
            board = humanMoveVision(board, video, board_lines) #watch and process the human move
            cv2.destroyAllWindows()
            computersTurn=True              #human's move is over

        drawLastMove(board)                #this finds the last move and gets the robot to draw it

        GameList[rootBoard(board)]=0        #record the move (for analysis later)
        if isGameWon(board)!="N":           #check to see if the game is over
            break    
    
    #when the game is over, declare the winner
    print("")
    gameResult = altIsGameWon(board)
    if gameResult=="D":
        print("The game was a draw")
    else:
        uArmFunctions.drawWinLine(uArm, winLine)
        if computersTurn==True:              #if the human won, the board still needs to be displayed
            printBrd(board)
        print(gameResult, "wins!")

    print("")
    learnFromGame(GameList)                 #remember all the moves from the game for next time!
    saveExperience()                        #save experience to file
    gameCount = gameCount + 1
    print("Game Count = ", gameCount)       #how many games have been played?
        
    computerGoesFirst = not computerGoesFirst   #take turns at going first
    #printExperience()                       #display the experience lists (optional - uncomment if wanted)
    
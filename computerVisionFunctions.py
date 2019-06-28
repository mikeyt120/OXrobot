import cv2             #opencv library
import numpy as np     #opencv library support
import time            #for time delays

"""%%%%%%%%%%%%%%%% COMPUTER VISION FUNCTIONS %%%%%%%%%%%%%%%%"""
'''Cycles through 10 frames of the video to flush out the older frames such that the live frames are being shown
without this function the frames from the last video.read() are initially shown.
I assume the buffer for the webcam isn't always up to date'''
def refreshWebcam(video):
    count_vid = 0
    # refresh the video stream
    while count_vid < 10:
        _, refresh_image = video.read()
        cv2.imshow("Robot thinking", refresh_image)
        cv2.waitKey(10)
        count_vid = count_vid + 1
    
'''function that takes in the video variable (e.g. cap) and returns whether the player has drawn anything (True or False).
Also returns the row and column of the players move if they drew on the board.'''
def checkPlayerMove(video, board_lines, original_image):

    #get snapshot of gameboard before the player makes their move
    refreshWebcam(video)
    _, game_board_check = video.read()
    
    # highest y coordinate
    intersection_bottom_left = [0, 0]
    for intersection in board_lines:
        if intersection.pt[1] > intersection_bottom_left[1]:
            intersection_bottom_left[0] = int(intersection.pt[0])
            intersection_bottom_left[1] = int(intersection.pt[1])

    # highest x coordinate
    intersection_bottom_right = [0, 0]
    for intersection in board_lines:
        if intersection.pt[0] > intersection_bottom_right[0]:
            intersection_bottom_right[0] = int(intersection.pt[0])
            intersection_bottom_right[1] = int(intersection.pt[1])

    # lowest x coordinate
    intersection_top_left = [game_board_check.shape[0], 0]
    for intersection in board_lines:
        if intersection.pt[0] < intersection_top_left[0]:
            intersection_top_left[0] = int(intersection.pt[0])
            intersection_top_left[1] = int(intersection.pt[1])

    # lowest y coordinate
    intersection_top_right = [0, game_board_check.shape[1]]
    for intersection in board_lines:
        if intersection.pt[1] < intersection_top_right[1]:
            intersection_top_right[0] = int(intersection.pt[0])
            intersection_top_right[1] = int(intersection.pt[1])

    #draw game_board lines
    #find gradient and y-intercept for each line, then find bounding corrdinates by using the edges of the image.

    #m = (y2-y1)(x2-x1)
    #c = y1 - m*x1
    #y = mx+c

    #top horizontal line
    horiz_top_m = (intersection_top_left[1] - intersection_top_right[1])/(intersection_top_left[0] - intersection_top_right[0])
    horiz_top_c = intersection_top_left[1] - horiz_top_m*intersection_top_left[0]
    #plot the line
    for i in range(0,game_board_check.shape[1], 1):
        cv2.circle(game_board_check, (i, int(horiz_top_m*i + horiz_top_c)), 1, (0, 0, 255), 2)

    #bottom horizontal line
    horiz_bottom_m = (intersection_bottom_left[1] - intersection_bottom_right[1]) / (
                intersection_bottom_left[0] - intersection_bottom_right[0])
    horiz_bottom_c = intersection_bottom_left[1] - horiz_bottom_m * intersection_bottom_left[0]
    # plot the line
    for i in range(0, game_board_check.shape[1], 1):
        cv2.circle(game_board_check, (i, int(horiz_bottom_m * i + horiz_bottom_c)), 1, (0, 0, 255), 2)

    # right vertical line
    vert_right_m = (intersection_top_right[1] - intersection_bottom_right[1]) / (
                intersection_top_right[0] - intersection_bottom_right[0])
    vert_right_c = intersection_top_right[1] - vert_right_m * intersection_top_right[0]
    # plot the line
    for i in range(0, game_board_check.shape[1], 1):
        cv2.circle(game_board_check, (i, int(vert_right_m * i + vert_right_c)), 1, (0, 0, 255), 2)

    # left vertical line
    vert_left_m = (intersection_top_left[1] - intersection_bottom_left[1]) / (
                intersection_top_left[0] - intersection_bottom_left[0])
    vert_left_c = intersection_top_left[1] - vert_left_m * intersection_top_left[0]
    # plot the line
    for i in range(0, game_board_check.shape[1], 1):
        cv2.circle(game_board_check, (i, int(vert_left_m * i + vert_left_c)), 1, (0, 0, 255), 2)

    cv2.imshow("Robot thinking", game_board_check)
    cv2.waitKey(50) #delay helps python show the image
    
    #prompt the player to make their move
    print("\nPlayer, please draw your move.\n")

    #detect hand movement
    #every second, get the robot arm to take another picture of the gameboard and save it
    #after period of no movement, exit the loop. Either a player_move_image will be saved or it wont
    no_movement_count = 0
    general_count = 0
    movement = True
    
    _, movement_image = video.read()
    _, current_image = video.read()
    while movement:
        _, current_image = video.read()
        #if the images have changed, reset the movement counter
        frame_diff = cv2.subtract(movement_image, current_image)
        hsv = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2HSV)
        lower_colour = np.array([0, 100, 30])
        upper_colour = np.array([255, 255, 255])
        diff_mask_noisy = cv2.inRange(hsv, lower_colour, upper_colour)
        #now reduce noise
        diff_mask_noisy_erode = cv2.erode(diff_mask_noisy, (10,10))
        diff_mask = cv2.morphologyEx(diff_mask_noisy_erode, cv2.MORPH_OPEN, (30, 30))
        
        cv2.imshow("Robot thinking", diff_mask)
        cv2.waitKey(100)
        
        if general_count == 0:
            pass #first time around has issues with the image
        elif cv2.sumElems(cv2.sumElems(diff_mask))[0] > 20000:
            #print(str(cv2.sumElems(cv2.sumElems(frame_diff))[0]))
            print("movement detected\n")
            no_movement_count = 0
        #if no movement after 5 seconds then break the loop
        elif no_movement_count >= 10:
            print("no more movement\n")
            movement = False
        #else add to the counter to track no movement
        else:
            no_movement_count = no_movement_count + 1

        movement_image = current_image
        general_count = general_count + 1

    print("Please stop drawing and stay clear of the camera.\n")
    #now it is assumed the hand has stopped drawing, check if anything was drawn
    player_move_image = cv2.subtract(original_image, current_image)

    #threshold the movement image such that only the coloured parts are kept.
    hsv = cv2.cvtColor(player_move_image, cv2.COLOR_BGR2HSV)
    lower_colour = np.array([0,100,30])
    upper_colour = np.array([255,255,255])
    mask_noisy = cv2.inRange(hsv, lower_colour, upper_colour)
    #now reduce noise
    mask_noisy_erode = cv2.erode(mask_noisy, (10,10))
    player_move_image_gray = cv2.morphologyEx(mask_noisy_erode, cv2.MORPH_OPEN, (30, 30))
       
    diff = False
    #A threshold of 10000 has been used as the sum of pixel intensity differences in the whole image
    # since lighting changes etc can make minor differences even if nothing has been drawn
    if cv2.sumElems(cv2.sumElems(player_move_image_gray))[0] > 10000:
        diff = True

    #if there has been a change
    if diff == True:
        cv2.imshow("Robot thinking", player_move_image_gray)
        cv2.waitKey(50) #gives python time to display image
        #now identify the row and column of the difference image centroid
        player_img_count = 0
        row_av = 0
        col_av = 0
        for k in range(len(player_move_image_gray)):
            for l in range(len(player_move_image_gray[k])):
                if player_move_image_gray[k][l] > 50:
                    player_img_count = player_img_count + 1
                    row_av = (row_av*(player_img_count - 1) + k)/player_img_count
                    col_av = (col_av*(player_img_count - 1) + l)/player_img_count

        #check which row position the players move is in
        if (horiz_top_m*col_av + horiz_top_c) > row_av:
            #then in the top row
            row = 1
        elif (horiz_bottom_m*col_av + horiz_bottom_c) > row_av:
            #then in middle row
            row = 2
        else:
            #then in bottom row
            row = 3

        # check which column position the players move is in
        if ((row_av - vert_left_c) / vert_left_m) > col_av:
            # then in the top row
            col = 1
        elif ((row_av - vert_right_c) / vert_right_m) > col_av:
            # then in middle row
            col = 2
        else:
            # then in bottom row
            col = 3

        return True, row, col
    else:
        print('Player did not draw anything')
        return False, 0, 0

# Gameboard Detection Variables
kernel_size = 5
kernel = np.ones((kernel_size, kernel_size), np.uint8)
minLength = 100
gap = 40

#blob parameter setup
blob_params = cv2.SimpleBlobDetector_Params()
blob_params.filterByArea = True
blob_params.minArea = 10 #how many pixels is acceptable per blob
blob_params.filterByCircularity = True
blob_params.minCircularity = 0.01
blob_params.filterByConvexity = True
blob_params.minConvexity = 0.01
blob_params.filterByInertia = True
blob_params.minInertiaRatio = 0.01

'''uses edge detection and morphology to detect the gameboard'''
def detect_gameboard(video_frame):

    input_img_gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)

    # find edges
    edges = cv2.Canny(input_img_gray, 80, 240)

    # dilate edges
    edges_dilation = cv2.dilate(edges, kernel, iterations=6)
    edges_erode = cv2.erode(edges_dilation, kernel, iterations=11)
    #above method only works to detect intersections if the camera angle is 45deg to the gameboard

    #below is a more advanced method which finds the lines, rather than the intersections.
    '''
    # hough transform
    #lines = cv2.HoughLinesP(edges_erode, 1, np.pi / 180, 1, minLineLength=minLength, maxLineGap=gap)

    #for line in lines:
    #    for x1, y1, x2, y2 in line:
    #        cv2.line(video_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    '''
    
    #find intersections using blob detection
    detector = cv2.SimpleBlobDetector_create(blob_params)
    frame_BW = cv2.bitwise_not(edges_erode)
    keypoints = detector.detect(frame_BW)
    # draw blobs on image
    im_with_blobs = cv2.drawKeypoints(video_frame, keypoints, np.array([]), (0, 0, 255),
                                      cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    cv2.imshow("Robot thinking", im_with_blobs)
    cv2.waitKey(50)
    
    #check if 4 line intersectinos are found
    if len(keypoints) == 4:
        return True, keypoints
    else:
        return False, 0

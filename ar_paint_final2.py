#para os argumentos iniciais dos limites
import argparse
from ast import Param
from asyncio.base_futures import _FINISHED
import colorsys
from copy import deepcopy
from tkinter import Canvas, Frame
from turtle import color
import cv2
from textwrap import indent
import json
import os
from color_segmenter_2_final2 import *
from collections import Counter
import math

# It stores the mouse position in global variables
drawing = False
drawingHand = True

flag = 0

def onMouse(event,x,y,flags,param):

    global ix,iy, drawing


    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(paintWindow,(int(x),int(y)),10,(0,0,255),-1)
        ix,iy = x,y

        drawingHand = False
        drawing = True
        mouse_location = (ix,iy)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            cv2.line(paintWindow, (ix, iy), (x, y), (0,0,250), thickness=thickness)
            ix, iy = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        

def movement():
    if drawingHand == True:
        global colors, colorIndex

        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]# blue green red
        colorIndex = 0 #default blue color

        if colorIndex == 0:
                bpoints.append(center)
                if len(bpoints)>2:
                    p1=bpoints[-2]
                    p2=bpoints[-1]
                    cv2.line(paintWindow, p1, p2, colors[colorIndex], thickness)

        elif colorIndex == 1:
            gpoints.append(center)
            if len(gpoints)>2:
                p1=gpoints[-2]
                p2=gpoints[-1]
                cv2.line(paintWindow,p1 ,p2 , colors[colorIndex], thickness)

        elif colorIndex == 2:
            rpoints.append(center)
            if len(rpoints)>2:
                p1=rpoints[-2]
                p2=rpoints[-1]
                cv2.line(paintWindow,p1 ,p2 , colors[colorIndex], thickness)

        


def onModes(usp):
    if usp == True:
        return 'usp_mode'




def main():
    global bpoints, gpoints,rpoints
    global thickness, paintWindow, frame
    global center, radius


    
    parser = argparse.ArgumentParser(description='PSR augmented reality paint') #creates a argumentParser object
    parser.add_argument('-j','--json', type=str, required = True, help='Full path to json file') 
    parser.add_argument('-usp','--use_shake_prevention',action='store_true', help='To use shake prevention.')
    
    
    args = vars(parser.parse_args())


    limits_values = open(args['json'])
    limits_values = json.load(limits_values)
    


    # extract variables from the file 
    min_B=  limits_values['limits']['B']['min']
    min_G = limits_values['limits']['G']['min']
    min_R = limits_values['limits']['R']['min']
    max_B = limits_values['limits']['B']['max']
    max_G = limits_values['limits']['G']['max']
    max_R = limits_values['limits']['R']['max']

    lower_bound=np.array([min_B,min_G,min_R])
    upper_bound=np.array([max_B,max_G,max_R])

    # Giving different arrays to handle colour points of different colours
    bpoints = []
    gpoints = []
    rpoints = []

    thickness = 1
    video_flag = 0

    #starting the painting window setup
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]# blue green red
    colorIndex = 0 #default blue color
    
    # White canvas
    canvas = np.ones((10,10),np.uint8)
    paintWindow = np.zeros((471,636,3)) + 255

        

    # Setup da câmara
    video_capture = cv2.VideoCapture(0)


    while True: 
    
        _, frame = video_capture.read()
        vid_thresh = frame.copy()
        vid_mask=cv2.inRange(vid_thresh,lower_bound, upper_bound)


        #add some dialation to increase segmented area
        Mask = cv2.erode(vid_mask, canvas, iterations=1)
        Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, canvas)
        Mask = cv2.dilate(Mask, canvas, iterations=1)
        
        #find all the contours of the segmented mask
        cnts,_ = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        mode = onModes(args['use_shake_prevention'])
        
        #checking if any countor is detected then ru the following statements
        if (past_x,past_y) == (0,0):
            (past_x,past_y) == center
        

        if len(cnts) > 0:
            # sorting the contours to find biggest contour
            cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
                
            # Get the radius of the enclosing circle around the found contour
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
                
            # Draw the circle around the contour
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            #cv2.circle(paintWindow, (int(x), int(y)), 1, (0, 0, 255), 2)

            # Calculating the center of the detected contour
            M = cv2.moments(cnt)

            
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))
            


            if drawingHand == True:
                movement()


        if args['use_shake_prevention'] is True:
            shake_prevention(x, y, past_x, past_y)
            
            
        k=cv2.waitKey(1)

        if k == 99:  # c clean the drawing
            print('clean paint')
            bpoints = []
            gpoints = []
            rpoints = []
            paintWindow = np.zeros((471,636,3)) + 255

        elif k== ord('b'):
            print('change color: blue')
            colorIndex = 0      
        elif k == ord('g'):
            print('change color: green')
            colorIndex = 1
        elif k == ord('r'):
            print('change color: red')
            colorIndex = 2

        elif k == ord('+'):
            print('thickness +')
            thickness += 1
        elif k == ord('-'):
            if thickness> 1:
                print('thicknes -')
                thickness -= 1
            else:
                print('is the minimum thickness')

        elif k == ord('w'):
            print('write actual image')
            cv2.imwrite(time.ctime().replace(' ','_')+'.png',paintWindow)
        elif k ==ord('q'):
            print('exit')
            exit(0)
        elif k == ord('m'):
            print('Use mouse to define pencil localization')
            if  args['use_shake_prevention'] == True:
                shake_prevention(x, y, past_x, past_y)
            cv2.setMouseCallback('Paint',onMouse)

        
        color = colors[colorIndex]
  
    
        cv2.imshow("Tracking", frame)
        cv2.imshow("Paint", paintWindow)
        cv2.imshow("mask",Mask)




def distance(current_location, previous_location):
    return int(math.sqrt(
        math.pow(current_location[0] - previous_location[0], 2) + math.pow(current_location[1] - previous_location[1],
                                                                           2)))
                                                                    

def shake_prevention(x, y, past_x, past_y):
    # Distancia ponto atual ao ponto anterior
    if past_x and past_y:
        # Se a distancia for superior a 50 retorna que é necessário fazer shake prevention caso contrario retorna que não é necessário
        if distance((x, y), (past_x, past_y)) > 100:
            return True
        return False

 

if __name__ == '__main__':
    main()
import argparse
from copy import deepcopy
from operator import index
from re import T
from xmlrpc.client import TRANSPORT_ERROR
import cv2
from textwrap import indent
import json
import os
from color_segmenter import *
from collections import deque
from functions import *
import copy


def main():
    
    parser = argparse.ArgumentParser(description='PSR augmented reality paint') #creates a argumentParser object
    parser.add_argument('-j','--json', type=str, required = True, help='Full path to json file') 
    parser.add_argument('-usp','--use_shake_prevention',action='store_true', help='To use shake prevention.')
    
    
    args = vars(parser.parse_args())
    
    #print com todos os comando possíveis para facilitar a utilização do programa ao utilizador
    program_instructions()



    limits_values = open(args['json'])
    limits_values = json.load(limits_values)
    
    paiting_images={'fish.jpg': 'fish.jpg','ice_cream.jpg': 'ice_cream.jpg'}

    # extract variables from the file 
    min_B=  limits_values['limits']['B']['min']
    min_G = limits_values['limits']['G']['min']
    min_R = limits_values['limits']['R']['min']
    max_B = limits_values['limits']['B']['max']
    max_G = limits_values['limits']['G']['max']
    max_R = limits_values['limits']['R']['max']

    lower_bound=np.array([min_B,min_G,min_R])
    upper_bound=np.array([max_B,max_G,max_R])

    rgb_points=[]
    thick_points=[]
    color_points=[]
    thickness=1

    #starting the painting window setup
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]# blue green red
    colorIndex = 0 #default blue color
    
    kernel = np.ones((10,10),np.uint8)

    paintWindow = np.zeros((471,636,3)) + 255
    paintWindow = cv2.flip(paintWindow, 1)

    center = None

    square_mode=False
    ellipse_mode=False
    first_press=False
    debouncing=0
    last_point_rect=[]
    last_point_circle=[]
    my_rect=[]
    my_circle=[]

    video_capture = cv2.VideoCapture(0)

    while True: 
    
        _, frame = video_capture.read()
        vid_thresh = frame.copy()
        vid_mask=cv2.inRange(vid_thresh,lower_bound, upper_bound)
        frame = cv2.flip(frame, 1)

        #Fuzzy detections that result in little blobs are cleared leaving only bigger objects detected
        Mask, x, y= removeSmallComponents(vid_mask, 400)

        Mask = cv2.flip(Mask, 1)
        
        #find all the contours of the segmented mask
        cnts,_ = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        
        #checking if any countor is detected then ru the following statements
        if len(cnts) > 0:
            # sorting the contours to find biggest contour
            cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
            
            cv2.line(frame, (int(x) - 10, int(y) + 10), (int(x) + 10, int(y) - 10), (0, 0, 255), 5)
            cv2.line(frame, (int(x) + 10, int(y) + 10), (int(x) - 10, int(y) - 10), (0, 0, 255), 5)

            
            # Calculating the center of the detected contour
            M = cv2.moments(cnt)
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

            rgb_points.append(center)
            #store for each point also the color and the thickness
            color_points.append(colorIndex)
            thick_points.append(thickness)

            # draw stuff
            if len(rgb_points) > 2 :
                # if square_mode == False and ellipse_mode == False:
                #     p1=rgb_points[-2]
                #     p2=rgb_points[-1]
                #     #cv2.line(paintWindow,p1 ,p2 , colors[colorIndex], thickness)
                # if square_mode == True:
                #     cv2.rectangle(paintWindow, actual_point, rgb_points[-1], colors[colorIndex], thickness)
                # if ellipse_mode == True:
                #     radius= max(abs(actual_point[0]-rgb_points[-1][0]),abs(actual_point[1]-rgb_points[-1][1]))
                #     cv2.circle(paintWindow, actual_point, radius, colors[colorIndex], thickness)
                
                #clean and draw every time the line, only if activated draw rect or circle

                if square_mode == False and ellipse_mode == False:
                    paintWindow = np.zeros((471,636,3)) + 255
                    for k in range(1,len(rgb_points)-1):
                        if max(abs(rgb_points[k-1][0]-rgb_points[k][0]),abs(rgb_points[k-1][1]-rgb_points[k][1])) > 30 : #if two points are too much distant is an error
                            continue
                        cv2.line(paintWindow, rgb_points[k - 1], rgb_points[k], colors[color_points[k]], thick_points[k])
                    for k in my_rect:
                        cv2.rectangle(paintWindow, k[0], k[1], colors[k[2]], k[3])
                    for k in my_circle:
                        cv2.circle(paintWindow, k[0],k[1], colors[k[2]], k[3])

                if square_mode == True:
                    paintWindow = np.zeros((471,636,3)) + 255
                    for k in range(1,rgb_points.index(actual_point)):#redraw everything
                        if max(abs(rgb_points[k-1][0]-rgb_points[k][0]),abs(rgb_points[k-1][1]-rgb_points[k][1])) > 30 : #if two points are too much distant is an error
                            continue
                        cv2.line(paintWindow, rgb_points[k - 1], rgb_points[k], colors[color_points[k]], thick_points[k])
                    for k in my_rect:
                        cv2.rectangle(paintWindow, k[0], k[1], colors[k[2]], k[3])
                    for k in my_circle:
                        cv2.circle(paintWindow, k[0],k[1],colors[k[2]], k[3])

                    cv2.rectangle(paintWindow, actual_point, rgb_points[-1], colors[colorIndex], thickness)
                    pt=(actual_point,rgb_points[-1], colorIndex, thickness)
                    last_point_rect.append(pt)
                    rgb_points.pop(-1) #avoid to draw line while drawing figure
                    color_points.pop(-1)
                    thick_points.pop(-1)

                if ellipse_mode == True:
                    paintWindow = np.zeros((471,636,3)) + 255
                    for k in range(1,rgb_points.index(actual_point)):#redraw everything
                        if max(abs(rgb_points[k-1][0]-rgb_points[k][0]),abs(rgb_points[k-1][1]-rgb_points[k][1])) > 30 : #if two points are too much distant is an error
                            continue
                        cv2.line(paintWindow, rgb_points[k - 1], rgb_points[k], colors[color_points[k]], thick_points[k])
                    for k in my_rect:
                        cv2.rectangle(paintWindow, k[0], k[1], colors[k[2]], k[3])
                    for k in my_circle:
                        cv2.circle(paintWindow, k[0],k[1], colors[k[2]], k[3])

                    radius= max(abs(actual_point[0]-rgb_points[-1][0]),abs(actual_point[1]-rgb_points[-1][1]))
                    cv2.circle(paintWindow, actual_point, radius, colors[colorIndex], thickness)
                    pt=(actual_point, radius, colorIndex, thickness)
                    last_point_circle.append(pt)
                    rgb_points.pop(-1) #avoid to draw line while drawing figure
                    color_points.pop(-1)
                    thick_points.pop(-1)



        frame_from_tracking= copy.copy(frame)
        video = frame.copy()
        frame_from_tracking[(Mask == 255)] = (0, 0, 255)

        k=cv2.waitKey(1)
        if k == 99:  # c clean the drawing
            print('clear paint window')
            rgb_points=[]
            color_points=[]
            thick_points=[]
            my_rect=[]
            my_circle=[]
            paintWindow = np.zeros((471,636,3)) + 255
        #change color
        elif k== ord('b'):
            print('change color: blue')
            colorIndex = 0      
        elif k == ord('g'):
            print('change color: green')
            colorIndex = 1
        elif k == ord('r'):
            print('change color: red')
            colorIndex = 2
        if k == ord('t'):
            #select a random painting from the dictionaryq
            path_to_image = random.choice(list(paiting_images.values()))
            draw = cv2.imread(path_to_image)
            cv2.imshow('DRAW', draw)
            path_color = list(paiting_images.keys())[list(paiting_images.values()).index(path_to_image)]
            print(path_color)
            img_color = cv2.imread(path_color)    
            
        #thickness
        elif k == ord('+'):
            print('thickness +')
            thickness += 1
        elif k == ord('-'):
            if thickness> 1:
                print('thicknes -')
                thickness -= 1
            else:
                print('is the minimum thickness')
        #write image
        elif k == ord('w'):
            print('write actual image')
            cv2.imwrite(time.ctime().replace(' ','_')+'.png',paintWindow)
        #exit
        elif k ==ord('q'):
            print('exit')
            exit(0)

        # drawing shapes
        #debouncing to read correctly the pression on the key
        elif k == ord('s'):# square drawing
            debouncing+=1
            if debouncing >= 1:
                if first_press == False:
                    first_press=True
                    print('drawing rectangle mode')
                    actual_point=center
                square_mode=True
                

        elif k == ord('o'):# ellipse drawing(circle)
            debouncing+=1
            if debouncing >=1:
                if first_press == False:
                    first_press=True
                    print('drawing ellipse mode')
                    actual_point=center
                ellipse_mode=True

        else :
            if debouncing>1:
                debouncing=0
                print('esc drawing mode')
                if len(last_point_rect)>0:
                    my_rect.append(last_point_rect[-1])
                    last_point_rect=[]
                if len(last_point_circle)>0:
                    my_circle.append(last_point_circle[-1])
                    last_point_circle=[]
                first_press=False
                square_mode=False
                ellipse_mode=False

        #paintWindow = cv2.flip(paintWindow, 1)
        cv2.imshow("Tracking", frame)
        cv2.imshow("Paint", paintWindow)
        cv2.imshow("mask",Mask)

if __name__ == '__main__':
    main()

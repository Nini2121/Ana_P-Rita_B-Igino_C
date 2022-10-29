#para os argumentos iniciais dos limites
import argparse
from copy import deepcopy
import cv2
from textwrap import indent
import json
import os
from color_segmenter import *
from collections import deque


def main():
    
    parser = argparse.ArgumentParser(description='PSR augmented reality paint') #creates a argumentParser object
    parser.add_argument('-j','--json', default='limits.json', dest="file", type=str, action="store", help='Full path to json file') 
    
    args = parser.parse_args()
    args = vars(args)

    if not os.path.exists(args["file"]):
        raise FileNotFoundError
        exit(0)
    else:
        limits_values = {}
        with open(args['file'], 'r') as f:
            limits_values = json.loads(f.readline())
        print(limits_values)

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
    # bpoints = [deque(maxlen=1024)]
    # gpoints = [deque(maxlen=1024)]
    # rpoints = [deque(maxlen=1024)]
    bpoints = []
    gpoints = []
    rpoints = []

    #assigning index values
    # blue_index = 0
    # green_index = 0
    # red_index = 0

    thickness=1

    #starting the painting window setup
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]# blue green red
    colorIndex = 0 #default blue color
    
    kernel = np.ones((10,10),np.uint8)

    paintWindow = np.zeros((471,636,3)) + 255

    center = None

    video_capture = cv2.VideoCapture(0)

    while True: 
        
        #k,frame,total_limits, vid_mask=cam_test(video_capture, max_B,min_B,max_G,min_G,max_R,min_R)
        _, frame = video_capture.read()
        vid_thresh = frame.copy()
        vid_mask=cv2.inRange(vid_thresh,lower_bound, upper_bound)

        #add some dialation to increase segmented area
        Mask = cv2.erode(vid_mask, kernel, iterations=1)
        Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, kernel)
        Mask = cv2.dilate(Mask, kernel, iterations=1)
        
        #find all the contours of the segmented mask
        cnts,_ = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        
        #checking if any countor is detected then ru the following statements
        if len(cnts) > 0:
            # sorting the contours to find biggest contour
            cnt = sorted(cnts, key = cv2.contourArea, reverse = True)[0]
            
            # Get the radius of the enclosing circle around the found contour
            ((x, y), radius) = cv2.minEnclosingCircle(cnt)
            
            # Draw the circle around the contour
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            
            # Calculating the center of the detected contour
            M = cv2.moments(cnt)
            center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

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

        
        #in this way every frame you re-paint the whole vector of points------------->is correct to draw every frame

        # points = [bpoints, gpoints, rpoints] 
        # for i in range(len(points)):
        #     for j in range(len(points[i])):
        #         for k in range(1, len(points[i][j])):
        #             if points[i][j][k - 1] is None or points[i][j][k] is None:
        #                 continue
        #             cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], thickness)
        #             cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], thickness)

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

        cv2.imshow("Tracking", frame)
        cv2.imshow("Paint", paintWindow)
        cv2.imshow("mask",Mask)

if __name__ == '__main__':
    main()
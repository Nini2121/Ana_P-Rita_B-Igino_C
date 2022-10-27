#para os argumentos iniciais dos limites
import argparse
import cv2
from textwrap import indent
import json
import os
from color_segmenter import *
from collections import deque


#função para a definição dos limites do código e das condições iniciais
def arg():
    parser = argparse.ArgumentParser(description='PSR augmented reality paint') #creates a argumentParser object
    parser.add_argument('-j','--json', default='limits.json', dest="file", type=str, action="store", help='Full path to json file') 
    
    args = parser.parse_args() #parse the , presents the scheme shown whith all the information
    
    #creates a dictionary 
    return vars(args)


def main():
    
    #--------
    #Initialization
    #---------
    args = arg()

    if not os.path.exists(args["file"]):
        raise FileNotFoundError

    limits_values = {}
    with open(args['file'], 'r') as f:
        limits_values = json.loads(f.readline())
    
    video_capture = cv2.VideoCapture(0)

    # extract variables from the file 
    
    min_B=  limits_values['limits']['B']['min']
    min_G = limits_values['limits']['G']['min']
    min_R = limits_values['limits']['R']['min']
    max_B = limits_values['limits']['B']['max']
    max_G = limits_values['limits']['G']['max']
    max_R = limits_values['limits']['R']['max']
    

    # Giving different arrays to handle colour points of different colours
    bpoints = [deque(maxlen=1024)]
    gpoints = [deque(maxlen=1024)]
    rpoints = [deque(maxlen=1024)]
   

    #assigning index values
    blue_index = 0
    green_index = 0
    red_index = 0

    tn=1
   
        

    #starting the painting window setup
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
    colorIndex = 0
    kernel = np.ones((5,5),np.uint8)

    paintWindow = np.zeros((471,636,3)) + 255
    cv2.namedWindow('Paint', cv2.WINDOW_AUTOSIZE)

    

    
    #----------- starting to get the segmentation of the object 
    if not os.path.exists(args["file"]):
        raise FileNotFoundError
    else:
        while True: 
            k,frame,total_limits=cam_test(video_capture, max_B,min_B,max_G,min_G,max_R,min_R)
            #Flipping the frame just for convenience
            frame = cv2.flip(frame, 1)

            pencil = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)



            # Change the valeus through color segmenter program
            lower_bound = np.array([min_B,min_G,min_R])
            upper_bound = np.array([max_B,max_G,max_R])



            Mask = cv2.inRange(pencil, lower_bound, upper_bound)
            Mask = cv2.erode(Mask, kernel, iterations=1)
            Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, kernel)
            Mask = cv2.dilate(Mask, kernel, iterations=1)

            cnts,_ = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL,
    	    cv2.CHAIN_APPROX_SIMPLE)
            center = None
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

                # Lacking: the code part were the keyboard change the color of the pencil!

                if key == 99:  # c clean the drawing
                    print('you pressed c')
                    bpoints = []
                    gpoints = []
                    rpoints = []
                    ypoints = []
                elif key == ord('b'):
                    print('change color: blue')
                    colorIndex == 0      
                elif key == ord('g'):
                    print('change color: green')
                    colorIndex == 1
                elif key == ord('r'):
                    print('change color: red')
                    colorIndex == 2
                elif key == ord('+'):
                    print('thickness +')
                    tn += 1
                elif key == ord('-'):
                    if tn > 1:
                        print('thicknes -')
                        tn -= 1
                    else:
                        print('is the minimum thickness')
                elif key == ord('w'):
                    print('write actual image')
                    print(time.ctime().replace(' ','_'))
                    #cv2.imwrite(+'.png',image)
                elif key ==ord('q'):
                    exit(0)

                if colorIndex == 0:
                    bpoints[blue_index].appendleft(center)
                elif colorIndex == 1:
                    gpoints[green_index].appendleft(center)
                elif colorIndex == 2:
                    rpoints[red_index].appendleft(center)
            else:
                bpoints.append(deque(maxlen=512))
                blue_index += 1
                gpoints.append(deque(maxlen=512))
                green_index += 1
                rpoints.append(deque(maxlen=512))
                red_index += 1
        
    #--------
    #Execution
    #---------
  
    #--------
    #Processing 
    #---------

    #--------
    #Visualization 
    #---------

    #--------
    #Termination
    #---------
if __name__ == '__main__':
    main()

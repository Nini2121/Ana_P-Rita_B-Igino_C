from copy import deepcopy
import cv2
import numpy as np
from colorama import Fore,Style
from functools import partial
import time

def mouseCallback(event,x,y,flags,userdata,options):

    if event == cv2.EVENT_MBUTTONDOWN:
        print('event was a buttondown')
        if options['is_drawing']:
            print('stop drawing')
            options['is_drawing'] = False
            options['xs']=[]
            options['ys']=[]
        else:
            print('start drawing')
            options['is_drawing']= True

    elif event == cv2.EVENT_MOUSEMOVE:
        if options['is_drawing']:
            options['xs'].append(x)
            options['ys'].append(y)

            if len(options['xs'])>2:

                x1=options['xs'][-2]
                y1=options['ys'][-2]
                x2=options['xs'][-1]
                y2=options['ys'][-1]
                cv2.line(options['gui_image'],(x1,y1),(x2,y2),options['pencil_color'],options['pencil_thick'])

def main():

    options={'is_drawing' : False,
            'xs':[],
            'ys':[],
            'gui_image':None,
            'pencil_color':(0,255,0),
            'pencil_thick':1}

    image= cv2.imread('/home/igino/Desktop/PSR/aula 5/atlascar.png')

    options['gui_image'] = deepcopy(image)
    window_name = 'window'
    cv2.namedWindow(window_name,cv2.WINDOW_AUTOSIZE)
    cv2.resizeWindow(window_name,800,400)

    cv2.setMouseCallback(window_name,partial(mouseCallback,options=options))


    while True:#esc to exit

        cv2.imshow(window_name,options['gui_image'])
        key=cv2.waitKey(30)

        if key == 99:# c clean the drawing
            print(Fore.RED+'you pressed c'+Style.RESET_ALL)
            xs=[]
            ys=[]
            options['gui_image']=deepcopy(image)
        elif key == ord('b'):
            print('change color: blue')
            options['pencil_color']=(255,0,0)
        elif key == ord('g'):
            print('change color: green')
            options['pencil_color']=(0,255,0)
        elif key == ord('r'):
            print('change color: red')
            options['pencil_color']=(0,0,255)
        elif key == ord('+'):
            print('thickness +')
            options['pencil_thick'] += 1
        elif key == ord('-'):
            if options['pencil_thick'] > 1:
                print('thicknes -')
                options['pencil_thick'] -= 1
            else:
                print('is the minimum thickness')
        elif key == ord('w'):
            print('write actual image')
            print(time.ctime().replace(' ','_'))
            #cv2.imwrite(+'.png',image)
        elif key ==ord('q'):
            exit(0)



if __name__ == '__main__':
    main()
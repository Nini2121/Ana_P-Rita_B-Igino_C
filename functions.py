import cv2
import numpy as np
from colorama import Fore, Back, Style
from enum import Enum
import math

def program_instructions():
    print(Style.BRIGHT + 'Function of every key:')
    print(Style.BRIGHT + 'Colors:')
    print(Style.BRIGHT + Fore.RED + 'Red: ' + Style.RESET_ALL + 'r')
    print(Style.BRIGHT + Fore.BLUE + 'Blue: ' + Style.RESET_ALL + 'b')
    print(Style.BRIGHT + Fore.GREEN + 'Green: ' + Style.RESET_ALL + 'g\n')
    print(Style.BRIGHT + 'Thickness:')
    print(Style.BRIGHT + 'More thickness: ' + Style.RESET_ALL + '+')
    print(Style.BRIGHT + 'Less thickness: ' + Style.RESET_ALL + '-\n')
    #print(Style.BRIGHT + 'Drawn with the mask: ' + Style.RESET_ALL + 'middle button hold')
    #print(Style.BRIGHT + 'Drawn with the mouse: ' + Style.RESET_ALL + 'left button hold\n')
    print(Style.BRIGHT + 'Shapes:')
    print(Style.BRIGHT + 'Squares: ' + Style.RESET_ALL + 's')
    print(Style.BRIGHT + 'Circles: ' + Style.RESET_ALL + 'f')
    print(Style.BRIGHT + 'Ellipses: ' + Style.RESET_ALL + 'e\n')
    print(Style.BRIGHT + 'Draw in a captured picture: ' + Style.RESET_ALL + 'p')
    print(Style.BRIGHT + 'Draw in the video: ' + Style.RESET_ALL + 'm')
    print(Style.BRIGHT + 'Paint-by-number test: ' + Style.RESET_ALL + 't')
    print(Style.BRIGHT + 'Accuracy of the test: ' + Style.RESET_ALL + 'v\n')
    print(Style.BRIGHT + 'Save image: ' + Style.RESET_ALL + 'w')
    print(Style.BRIGHT + 'Clear the canvas: ' + Style.RESET_ALL + 'c')
    print(Style.BRIGHT + 'Quit: ' + Style.RESET_ALL + 'q')
    #print(Style.BRIGHT + 'To see this panel again use: ' + Style.RESET_ALL + Back.YELLOW + Fore.BLACK + 'h' +
     #     Style.RESET_ALL)

def removeSmallComponents(image, threshold):
    # find all your connected components (white blobs in your image)
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(image, connectivity=8)
    sizes = stats[1:, -1]
    nb_components = nb_components - 1
    x = None
    y = None
    img2 = np.zeros(output.shape, dtype=np.uint8)

    # for every component in the image, you keep it only if it's above threshold
    for i in range(0, nb_components):
        if sizes[i] >= threshold:
            # to use the biggest
            x, y = centroids[i + 1]
            threshold = sizes[i]
            img2[output == i + 1] = 255

    return img2, x, y



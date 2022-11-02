
import numpy as np
import cv2


image = cv2.imread("fig1_merds.png")
image_solution = cv2.imread("fig1solution.png")
# Blue, green, reed


def evaluation(image,image_solution):
    
    boundaries = [((110, 50, 50), (130, 255, 255)), ((36, 25, 25), (70, 255, 255)), ((0, 0, 0), (9, 255, 255))]
    color_result = []
    Acc_by_color = {}

    for (lower, upper) in boundaries:

        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        image_solution = cv2.cvtColor(image_solution,cv2.COLOR_BGR2RGB)
            
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")

        width = image.shape[1]
        height = image.shape[0]

        dim = (width,height)

        image_solution = cv2.resize(image_solution, dim, interpolation = cv2.INTER_AREA)

        ## convert to hsv both our drawing and the painted one
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        color_used= cv2.inRange(rgb, lower, upper)

        rgb_s = cv2.cvtColor(image_solution, cv2.COLOR_BGR2RGB)
        color_real = cv2.inRange(rgb_s, lower, upper)


        # we also need to remove the small components from the painted mask
        kernel = np.ones((5, 5), np.uint8)

        color_real = cv2.erode(color_real, kernel, 1)
        color_real = cv2.dilate(color_real, kernel, 1)

        # the masks of every color
        # the part painted that is right
        bitwiseAnd = cv2.bitwise_and(color_real, color_used)

        # ALL THE Paint
        bitwiseor = cv2.bitwise_or(color_used,color_real)


        # calculus
        bitwiseor[bitwiseor > 0] = 1
        bitwiseAnd[bitwiseAnd > 0] = 1

        painted = sum(sum(bitwiseAnd))
        total = sum(sum(bitwiseor))

        acc  = (painted / total) * 100


        color_result.append(acc)

    print(color_result)

    Acc_by_color = {"Blue": color_result[0],"Green": color_result[1],"Red": color_result[2]}

    print("The accuracy of the paiting is:" + str(Acc_by_color))


evaluation(image,image_solution)
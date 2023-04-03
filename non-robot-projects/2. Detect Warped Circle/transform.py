import numpy as np
import cv2

# READ IMAGE
img = cv2.imread("transform.jpg")

# COORDINATES OF QUADRILATERAL
# p1 p2
# p3 p4
p1 = [950, 257]
p2 = [1832, 267]
p3 = [550, 837]
p4 = [1752, 800]
'''
# DRAW LINES BETWEEN THESE COORDINATES-------------------
cv2.line(img, p1, p2, (0, 0, 255), 1)
cv2.line(img, p3, p4, (0, 0, 255), 1)
cv2.line(img, p2, p4, (0, 0, 255), 1)
cv2.line(img, p1, p3, (0, 0, 255), 1)
#cv2.imshow("Original", img)
'''

# CREATES MATRIX FOR TRANSFORMATION
# coordinates of original quadrilateral
pts1 = np.float32([p1, p2, p3, p4])
# coordinates of new , with offset to make sure the whole screen shows
offsetX = 4500
offsetY = 2500
pts2 = np.float32([[0 + offsetX, 0 + offsetY], [2121 + offsetX, 0 + offsetY],
                   [0 + offsetX, 2150 + offsetY], [2121 + offsetX, 2150 + offsetY]])

# APPLY PERSPECTIVE TRANSFORM TO NEW IMAGE
transform_matrix = cv2.getPerspectiveTransform(pts1, pts2)
new_img = cv2.warpPerspective(img, transform_matrix, (8521, 6721))  # big window size to make sure nothing's cut off

# RESIZE NEW IMAGE
scale_percent = 60  # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)

new_img = cv2.resize(new_img, dim, interpolation=cv2.INTER_AREA)

# GRAYSCALE IMAGE
gray = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)

# DETECT CIRCLE
all_circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 1000, param1=50, param2=50, maxRadius=140)
if all_circles is not None:
    all_circles = np.round(all_circles[0, :]).astype("int")
    for (x, y, r) in all_circles:
        # DRAW CIRCLE AND ORIGIN ON NEW IMAGE
        cv2.circle(new_img, (x, y), r, (255, 0, 255), 6)
        cv2.circle(new_img, (x, y), 4, (255, 0, 255), -1)
        # stops loop from drawing a ton of circles after the first one is drawn
        if (x, y, r) in all_circles:
            break
# cv2.imshow('Transformed', new_img)  # show initial transformed image

# RESIZE NEW IMAGE AGAIN
scale = 500  # percent of original size
w = int(img.shape[1] * scale / 100)
h = int(img.shape[0] * scale / 100)
dim2 = (w, h)

new_img = cv2.resize(new_img, dim2, interpolation=cv2.INTER_AREA)

# TRANSFORM NEW IMAGE BACK
inv_matrix = cv2.getPerspectiveTransform(pts2, pts1)
# FINAL IMAGE GETS PERSPECTIVE BACK TO NORMAL
final_img = cv2.warpPerspective(new_img, inv_matrix, (3321, 2021)) # too big screen size makes image small

# SECOND SET OF POINTS TO WARP
p1 = [180,15]
p2 = [2658,20]
p3 = [730,1534]
p4 = [3218,1486]
""" # lines for testing
cv2.line(final_img, p1, p2, (0, 0, 255), 1)
cv2.line(final_img, p3, p4, (0, 0, 255), 1)
cv2.line(final_img, p2, p4, (0, 0, 255), 1)
cv2.line(final_img, p1, p3, (0, 0, 255), 1)
cv2.imshow("Lines", final_img)
"""
pts1 = np.float32([p1, p2, p3, p4])
pts2 = np.float32([[0, 0], [2121, 0],
                   [0, 1414], [2121, 1414]])

# TRANSFORM TO ORIGINAL
final_matrix = cv2.getPerspectiveTransform(pts1, pts2)
output = cv2.warpPerspective(final_img, final_matrix, (2121, 1414))
cv2.imwrite("output.jpg", output)
cv2.imshow("Please work", output)

cv2.waitKey(0)

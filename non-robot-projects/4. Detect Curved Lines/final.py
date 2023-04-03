import cv2
import numpy as np
import math

# READ IMAGE
image_name = input("Detect arrows on right.jpg or left.jpg? ")
img = cv2.imread(image_name)

# INITIALIZE TRIANGLE DIMENSIONS
WIDTH = 348
SIDE = WIDTH / math.sqrt(2)
HEIGHT = WIDTH/2

# ---------------------------------------- FUNCTIONS ----------------------------------------
def transform(p1, p2, p3, p4, offsetX, offsetY, inverse, new_img):
   # coordinates of original quadrilateral
   pts1 = np.float32([p1, p2, p3, p4])

   # coordinates of new , with offset to make sure the whole screen shows
   pts2 = np.float32([[0 + offsetX, 0 + offsetY], [2448 + offsetX, 0 + offsetY],
                      [0 + offsetX, 3264 + offsetY], [2448 + offsetX, 3264 + offsetY]])
   if inverse == False:
       transform_matrix = cv2.getPerspectiveTransform(pts1, pts2)
       new_img = cv2.warpPerspective(new_img, transform_matrix, (6021, 8021))  # big window size to make sure nothing's cut off
   elif inverse == True:
       transform_matrix = cv2.getPerspectiveTransform(pts2, pts1)
       new_img = cv2.warpPerspective(new_img, transform_matrix, (2448,3264))
       scale_percent1 = 20  # percent of original size
       width1 = int(img.shape[1] * scale_percent1 / 100)
       height1 = int(img.shape[0] * scale_percent1 / 100)
       dim1 = (width1, height1)
       new_img = cv2.resize(new_img, dim1, interpolation=cv2.INTER_AREA)
   return new_img


def blackout(b1, b2, C, image):
    contours = np.array([b1, b2, C])

    mask = np.zeros(image.shape, dtype=np.uint8)
    cv2.fillPoly(mask, pts=np.int32([contours]), color=(255,255,255))

    # apply the mask
    masked_image = cv2.bitwise_and(image, mask)
    return masked_image


def detect_lines(img):
    # GRAYSCALE, BLUR, AND GET EDGES
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel_size = 5
    gray = cv2.GaussianBlur(gray, (kernel_size, kernel_size), 0)
    low_threshold = 50
    high_threshold = 150
    edges = cv2.Canny(gray, low_threshold, high_threshold)

    # GET LINES
    rho = 1
    theta = np.pi / 180
    threshold = 15
    min_line_length = 15
    max_line_gap = 200
    line_image = np.copy(img) * 0  # creating a blank to draw lines on

    # run Hough on edge detected image
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                            min_line_length, max_line_gap)

    # draws lines on blank image
    slope_sum, count = 0,0
    endpoints = {}
    for line in lines:
        for x1, y1, x2, y2 in line:
            # max line length = 90
            if distance(x1, y1, x2, y2) < 90:
                cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 255), 5)
                if (x2-x1) != 0 and (y2-y1) != 0:
                    slope = (y2-y1)/(x2-x1)
                    slope_sum += slope
                    count += 1
                elif (x2-x1) == 0:
                    count = 0
                    break
    if count != 0:
        avg_slope = slope_sum / count
    else:
        avg_slope = "inf"

    # Draw the lines on the  image
    lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
    return lines_edges, avg_slope


def distance(x1,y1,x2,y2):
    dist = math.sqrt((x1-x2)**2 + (y1-y2)**2)
    return dist


def midpoint(pt1, pt2):
    x1,y1 = pt1
    x2,y2 = pt2
    mid = (int((x1 + x2) / 2), int((y1 + y2) / 2))
    return mid


def find_points(point_a, distance, m):
    a, b = point_a
    if m == "inf":
        x_plus = a
        y_plus = b - distance
        final = (int(x_plus), int(y_plus))
    else:
        a, b = point_a
        dx = math.sqrt(distance ** 2 / (m ** 2 + 1))
        dy = m * dx
        final = (int(a + dx), int(b - dy))
    return final


def get_standard(currC):
    newB1 = (int(currC[0] - WIDTH/2), currC[1])
    newB2 = (int(currC[0] + WIDTH/2), currC[1])
    newC = (currC[0], int(currC[1] - HEIGHT))
    """ horizontal
    newB1 = (currC[0], int(currC[1] - WIDTH/2))
    newB2 = (currC[0], int(currC[1] + WIDTH/2))
    newC = (int(currC[0] + HEIGHT), currC[1])
    """
    return newB1, newB2, newC


# rotate a point counterclockwise by a given angle in radians around a given origin.
def rotate(origin, point, angle):
    ox, oy = origin
    px, py = point

    qx = int(ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy))
    qy = int(oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy))
    return (qx, qy)

def draw_arrows(currB1, currB2, currC, num_arrows, small_img):
    # CREATE FINAL SMALL IMAGE TO DRAW ON
    final_small = np.copy(small_img)

    # REMEMBER: detect all lines on blackout_img (which references small_img), but will draw all lines on final_small
    for i in range(num_arrows):
        # blackout the image at current triangle, get avg slope of the path
        blackout_img = blackout(currB1, currB2, currC, small_img)
        # detects lines
        blackout_img, detected_slope = detect_lines(blackout_img)

        # draws arrow onto small image
        startpoint = midpoint(currB1, currB2)
        endpoint = find_points(startpoint, HEIGHT, detected_slope) # this causes C to go up and down, as find_points finds C in both directions

        # if y coordinate is lower than previous C and we are on the first half of the curve
        if endpoint[1] > currC[1] and endpoint[1] > 300 and i < 4:
            if endpoint[1] == 335:
                # exception at the precise turning point of the graph; reduce step size
                endpoint = (endpoint[0], int(endpoint[1] - HEIGHT*.8))
            else:
                # ensure we are always moving forward
                endpoint = (endpoint[0], int(endpoint[1] - HEIGHT*2 + HEIGHT/2))

        # else if we are on the turning point
        elif endpoint[1] < 400 and i==4:
            # constraint: when it would hit the line if the transformation was applied, don't make it go up so much
            if endpoint[1] == 290:
                endpoint = (endpoint[0], int(endpoint[1] - HEIGHT/1.8))
            else:
                # reduce step size of arrow
                endpoint = (int(endpoint[0] - HEIGHT/2), int(endpoint[1] - HEIGHT*1.1))

        # else if we are at at the horizontal half and y is too large, we reduce the length of our arrow
        elif i > 4 and endpoint[1]>200:
            endpoint = (endpoint[0], int(endpoint[1] - HEIGHT/2))

        cv2.circle(blackout_img,endpoint,10,(255,0,0), thickness=-1)
        cv2.arrowedLine(final_small, startpoint, endpoint, (255, 0, 0), 5)
        cv2.imshow("lines", blackout_img)

        # get angle to rotate around
        if detected_slope != "inf" and i != 4:
            theta = np.arctan(-1 / detected_slope)
        elif detected_slope != "inf" and i == 4:
            theta = math.pi/3
        else:
            theta = 0

        # GENERATE AND ROTATE NEXT TRIANGLE
        # standard triangle on top of current one
        newB1, newB2, newC = get_standard(endpoint)

        # rotates previously standard triangle by theta
        newB1 = rotate(endpoint, newB1, theta)
        newB2 = rotate(endpoint, newB2, theta)
        newC = rotate(endpoint, newC, theta)

        currB1, currB2, currC = newB1, newB2, newC
        cv2.circle(blackout_img, currC, 10, (255, 0, 0), thickness=-1)

    return final_small
   
# ---------------------------------------- PERSPECTIVE TRANSFORMATION ----------------------------------------
# GET POINTS AND OFFSET FOR TRANSFORMATION
p1 = (479,630)
p2 = (1869,621)
p3 = (169,2404)
p4 = (2138,2394)

offsetX = 1500
offsetY = 3000

# PARAMS TO RESIZE IMAGE (to be adjusted based on the computer running it)
scale_percent1 = 20  # percent of original size
width1 = int(img.shape[1] * scale_percent1 / 100)
height1 = int(img.shape[0] * scale_percent1 / 100)
dim1 = (width1, height1)

# APPLY PERSPECTIVE TRANSFORM TO NEW IMAGE AND CROP IT
new_img = transform(p1, p2, p3, p4, offsetX, offsetY, False, img)
new_img = cv2.resize(new_img, dim1, interpolation=cv2.INTER_AREA)

# APPLY MASK
# finding coordinates of ROI
x_start = 124
y_start = 236
width = 197
height = 255

start = (x_start, y_start)
end = (x_start + width, y_start + height)

# -------------------------------------- TRIANGLE GENERATION AND LINE DETECTING --------------------------------------
# CREATE SMALL IMAGE TO REFERENCE IN BLACKOUT
small_img = new_img[y_start:end[1],x_start:end[0]]
small_img = cv2.resize(small_img, (width*3, height*3))

# initializing triangle coordinates
currB1 = (0, height*3)
currB2 = (0 + WIDTH, height*3)
currC = (0 + WIDTH/2, height*3 - HEIGHT)

try:
    final_small = draw_arrows(currB1, currB2, currC, 7, small_img)
except TypeError:
    small_img = cv2.flip(small_img, 1)
    final_small = draw_arrows(currB1, currB2, currC, 6, small_img)
    final_small = cv2.flip(final_small, 1)

# shrink back to original size
final_small = cv2.resize(final_small, (197, 255))
# display result
cv2.imshow("test.jpg",final_small)
cv2.imwrite("test.jpg",final_small)

# PASTE FINAL SMALL IMAGE ONTO ORIGINAL IMAGE
new_img[y_start:end[1], x_start:end[0]] = final_small

# SHOW TRANSFORMED AND EDITED IMAGE
cv2.imshow("transformed and overlaid", new_img)

# PARAMS TO RESIZE IMAGE (to be adjusted based on the computer running it)
scale_percent1 = 246  # percent of original size
width1 = int(img.shape[1] * scale_percent1 / 100)
height1 = int(img.shape[0] * scale_percent1 / 100)
dim1 = (width1, height1)
new_img = cv2.resize(new_img, dim1, interpolation=cv2.INTER_AREA)

# INVERT THE TRANSFORMATION
inv_img = transform(p1, p2, p3, p4, offsetX, offsetY, True, new_img) # inverse transforms new image
cv2.imshow("Inv", inv_img)
cv2.imwrite("new" + image_name, inv_img)
cv2.waitKey(0)

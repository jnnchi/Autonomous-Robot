import cv2
import numpy as np

# READ IMAGE
name = input("Input the name of the image to detect: ")
img = cv2.imread(name)

# FUNCTION TO TRANSFORM THE IMAGE
def transform(p1, p2, p3, p4, offsetX, offsetY, inverse, new_img):
    # coordinates of original quadrilateral
    pts1 = np.float32([p1, p2, p3, p4])

    # coordinates of new , with offset to make sure the whole screen shows
    pts2 = np.float32([[0 + offsetX, 0 + offsetY], [3000 + offsetX, 0 + offsetY],
                       [0 + offsetX, 4000 + offsetY], [3000 + offsetX, 4000 + offsetY]])
    if inverse == False:
        transform_matrix = cv2.getPerspectiveTransform(pts1, pts2)
        new_img = cv2.warpPerspective(new_img, transform_matrix, (9021, 10021))  # big window size to make sure nothing's cut off
    elif inverse == True:
        transform_matrix = cv2.getPerspectiveTransform(pts2, pts1)
        new_img = cv2.warpPerspective(new_img, transform_matrix, (3000,4000))
    return new_img

# GET POINTS AND OFFSET FOR TRANSFORMATION
p1 = (665,890)
p2 = (2283,895)
p3 = (85,2945)
p4 = (2880,2925)

offsetX = 2500
offsetY = 4800

# APPLY TRANSFORM FUNCTION TO NEW IMAGE
new_img = transform(p1, p2, p3, p4, offsetX, offsetY, False, img)

# GRAY SCALE AND GET EDGES
gray = cv2.cvtColor(new_img,cv2.COLOR_BGR2GRAY)
kernel_size = 5
low_threshold = 50
high_threshold = 150
edges = cv2.Canny(gray, low_threshold, high_threshold)

# SET PARAMETERS FOR LINES
rho = 1  # distance resolution in pixels of the Hough grid
theta = np.pi / 180  # angular resolution in radians of the Hough grid
threshold = 1050  # minimum number of votes (intersections in Hough grid cell)
min_line_length = 4200  # minimum number of pixels making up a line
max_line_gap = 400  # maximum gap in pixels between connectable line segments
line_image = np.copy(new_img) * 0  # creating a blank to draw lines on
# GET LINES
# Output "lines" is an array containing endpoints of detected line segments
lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                        min_line_length , max_line_gap)

# dictionary of all endpoints of the lines
coords = {}

# FUNCTION TO DRAW ARROW
def draw_arrow(new_img,line_image, coords, left):
    ordered_coords = dict(sorted(coords.items(), key=lambda x: x[0]))
    x1 = min(ordered_coords.keys())
    xLast = max(ordered_coords.keys())
    if x1 > 5000:
        output = False
    else:
        output = True
        bottom_left = ordered_coords[x1][0]
        bottom_right = ordered_coords[xLast][0]
        top_left = ordered_coords[x1][1]
        top_right = ordered_coords[xLast][1]

        #cv2.line(line_image, bottom_left, top_left, (255, 0, 255), 5)
        #cv2.line(line_image, bottom_right, top_right, (255, 0, 255), 5)

        startpoint = [int((bottom_left[0] + bottom_right[0]) / 2), int((bottom_left[1] + bottom_right[1]) / 2)]
        endpoint = [int((top_left[0] + top_right[0]) / 2), int((top_left[1] + top_right[1]) / 2)]

        # DRAW DETECTED LINES
        new_img = cv2.addWeighted(new_img, 0.8, line_image, 1, 0)
        if left == False:
            cv2.arrowedLine(new_img, startpoint,endpoint, (255, 0, 255), 20)
        elif left == True:
            cv2.arrowedLine(new_img, endpoint, startpoint, (255, 0, 255), 20)
    return [new_img, output]

# appends coordinates of possible black lines to dict
for line in lines:
    for x1,y1,x2,y2 in line:
        #cv2.line(line_image,(x1,y1),(x2,y2),(255,0,255),5) # draws lines on blank image

        # excludes lines that are too close to edges of image (cuz they're the edges not the black lines)
        if x1<2000 or x1>5600:
            pass
        else:
            bottom = [int(x1),int(y1)]
            top = [int(x2),int(y2)]
            coords[bottom[0]] = [bottom, top]

# draws the arrow
final_img, output = draw_arrow(new_img,line_image, coords, False)
if output == False:
    lines = cv2.HoughLinesP(edges, rho, theta, 10, np.array([]),
                            40, max_line_gap)
    for line in lines:
        for x1, y1, x2, y2 in line:
            # cv2.line(line_image,(x1,y1),(x2,y2),(255,0,255),5)
            if x2<3000 or x1 > 5666:
                pass
            else:
                bottom = [int(x1), int(y1)]
                top = [int(x2), int(y2)]
                coords[bottom[0]] = [bottom, top]
    final_img = draw_arrow(new_img,line_image, coords, True)[0]

# TRANSFORM BACK
final_img = transform(p1, p2, p3, p4, offsetX, offsetY, True, final_img)

# RESIZE NEW IMAGE (to be adjusted based on the computer running it)
scale_percent = 20  # percent of original size
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
final_img = cv2.resize(final_img, dim, interpolation=cv2.INTER_AREA)

# SHOW FINAL IMAGE
cv2.imshow("Lines", final_img)
cv2.imwrite("new" + name, final_img)
cv2.waitKey(0)

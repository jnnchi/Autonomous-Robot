import numpy as np
import cv2
import math

def transform(p1, p2, p3, p4, offsetX, offsetY, inverse, new_img, height, width):
    # coordinates of original quadrilateral
    pts1 = np.float32([p1, p2, p3, p4])

    # coordinates of new , with offset to make sure the whole screen shows
    pts2 = np.float32([[0 + offsetX, 0 + offsetY], [width + offsetX, 0 + offsetY],
                      [0 + offsetX, height + offsetY], [width + offsetX, height + offsetY]])
    if not inverse:
        transform_matrix = cv2.getPerspectiveTransform(pts1, pts2)
        new_img = cv2.warpPerspective(new_img, transform_matrix, (3000, 3000))  # big window size to make sure nothing's cut off
    elif inverse:
        transform_matrix = cv2.getPerspectiveTransform(pts2, pts1)
        new_img = cv2.warpPerspective(new_img, transform_matrix, (width,height))
        scale_percent1 = 20  # percent of original size
        width1 = int(new_img.shape[1] * scale_percent1 / 100)
        height1 = int(new_img.shape[0] * scale_percent1 / 100)
        dim1 = (width1, height1)
        new_img = cv2.resize(new_img, dim1, interpolation=cv2.INTER_AREA)
    return new_img

def distance(x1,y1,x2,y2):
    dist = math.sqrt((x1-x2)**2 + (y1-y2)**2)
    return dist

# SOURCE: https://stackoverflow.com/questions/32609098/how-to-fast-change-image-brightness-with-python-opencv
def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img


# SOURCE: https://stackoverflow.com/questions/39308030/how-do-i-increase-the-contrast-of-an-image-in-python-opencv
def enhance(img):
    # converting to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)

    # Applying CLAHE to L-channel
    # feel free to try different values for the limit and grid size:
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)

    # merge the CLAHE enhanced L-channel with the a and b channel
    limg = cv2.merge((cl, a, b))

    # Converting image from LAB Color model to BGR color spcae
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    return enhanced_img


def resize(img, scale):
    scale_percent = scale  # percent of original size
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    # resize image
    resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    return resized


def detect_lines(img):
    # GET EDGES
    low_threshold = 50
    high_threshold = 150
    edges = cv2.Canny(img, low_threshold, high_threshold)

    # GET LINES
    rho = 1
    theta = np.pi / 180
    threshold = 60
    min_line_length = 5
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
            if distance(x1, y1, x2, y2) < 140:
                if (x2-x1) != 0 and (y2-y1) != 0:
                    cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 255), 5)
                    slope = (y2-y1)/(x2-x1)
                    slope_sum += slope
                    count += 1
    if count != 0:
        avg_slope = slope_sum / count
    else:
        avg_slope = "inf"

    # Draw the lines on the  image
    lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
    return lines_edges, avg_slope


if __name__ == "__main__":
    input_video = cv2.VideoCapture('train.mp4')
    frame_count = 0

    # CREATE OUTPUT VIDEO
    # SOURCE: https://www.geeksforgeeks.org/saving-a-video-using-opencv/
    size = (1152, 648)
    output_video = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, size)

    yellow, red = 0, 0
    # OPEN VIDEO
    # SOURCE: https://learnopencv.com/read-write-and-display-a-video-using-opencv-cpp-python/
    while input_video.isOpened():
        # READ VIDEO INTO FRAMES
        ret, frame = input_video.read()

        if ret:
            frame_count += 1
            # RESIZE, ENHANCE, and BRIGHTEN IMAGE
            frame = resize(frame, 60)
            newframe = enhance(frame)
            newframe = increase_brightness(newframe, value=10)
            # get image dimensions to use later
            height, width = frame.shape[0:2]

            # TURN IMAGE TO BINARY
            # SOURCE: https://stackoverflow.com/questions/62042172/how-to-remove-noise-in-image-opencv-python
            grayImage = cv2.cvtColor(newframe, cv2.COLOR_BGR2GRAY)
            se = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
            bg = cv2.morphologyEx(grayImage, cv2.MORPH_DILATE, se)
            out_gray = cv2.divide(grayImage, bg, scale=255)
            bwframe = cv2.threshold(out_gray, 0, 255, cv2.THRESH_OTSU)[1]

            # TRANSFORM BINARY IMAGE
            p1 = (150, 300)
            p2 = (616, 300)
            p3 = (0, height)
            p4 = (width - 400, height)
            offsetX = 1000
            offsetY = 1000
            trans_frame = transform(p1, p2, p3, p4, offsetX, offsetY, False, bwframe, height, width)
            trans_frame = resize(trans_frame, 50)

            # COORDINATES OF REGION OF INTEREST
            startpoint = (660, 680)
            endpoint = (1070, 820)
            # CROP TRANSFORMED IMAGE TO ROI
            crop_frame = trans_frame[startpoint[1]:endpoint[1], startpoint[0]:endpoint[0]]

            # DETECT LINES ON CROPPED FRAME
            crop_frame, avg_slope = detect_lines(crop_frame)

            color = (0, 255, 0)
            if avg_slope == "inf":
                color = (0, 255, 0)
            elif avg_slope > 10:
                color = (0, 255, 255)
                yellow += 1
            elif abs(avg_slope) > 1 and abs(avg_slope) < 2:
                color = (0, 255, 0)
            elif abs(avg_slope) > 0 and abs(avg_slope) < 1.8:
                color = (0, 255, 255)
                yellow += 1
            elif avg_slope < 0 or avg_slope > 30:
                color = (0, 255, 255)
                yellow += 1
            elif avg_slope == 0:
                color = (0,0,255)
                red+=1

            #cv2.putText(frame, str(avg_slope),(500, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_4)

            # ANNOTATE VIDEO WITH FRAME COUNT AND CIRCLE
            cv2.putText(frame, str(frame_count), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_4)
            cv2.circle(frame, center=(width-50, 50), radius=30, color=color, thickness=-1)

            # DISPLAY VIDEO
            # cv2.imshow("Binary", crop_frame) # shows line detection
            cv2.imshow("Original", frame)
            output_video.write(frame)

            # PRESS 0 TO EXIT
            if cv2.waitKey(25) & 0xFF == ord('0'):
                break
        # no more frames left
        elif not ret:
            print("Total number of frames: {}".format(frame_count))
            print((506-yellow-red)/506, yellow/506, red/506)
            break

    input_video.release()

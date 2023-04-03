import numpy as np
import cv2


# EDITS EACH FRAME OF THE VIDEO (detects and draws circle)
# parameters: image to edit, frame number (in relation to larger video)
# output: edited image, 0 or 1 depending on if the frame was found
def draw_circle(img, i):
    # GRAYSCALE IMAGE
    imggray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # IDENTIFY CIRCLES IN IMAGE
    all_circles = cv2.HoughCircles(imggray, cv2.HOUGH_GRADIENT, 1, 1000, param1=50, param2=30, minRadius=130)

    # COUNTS FRAMES THAT HAVE CIRCLES
    if_circle = 0

    # SOURCE: https://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
    # IF CIRCLE IS DETECTED IN IMAGE
    if all_circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        all_circles = np.round(all_circles[0, :]).astype("int")

        # print "Found" and frame number on console
        print("FOUND!! Frame {}".format(i))

        # "yes there is a circle on this frame" (counts)
        if_circle = 1

        # loops through detected circle ONE TIME and draws on it
        for (x, y, r) in all_circles:
            # draw circle outline and dot in the center
            cv2.circle(img, (x, y), r, (255, 0, 255), 4)
            cv2.circle(img, (x, y), 2, (255, 0, 255), -1)

            # stops loop from drawing a ton of circles after the first one is drawn
            if (x, y, r) in all_circles:
                break
    # IF NO CIRCLES DETECTED IN IMAGE
    else:
        # perform transformation if needed; in this case they were NOT needed
        # if_circle is defaulted to 0 (doesn't get counted in frames with circles)
        pass

    return [img, if_circle]


if __name__ == "__main__":
    # READS INPUT VIDEO
    input_video = cv2.VideoCapture('slowmo.mp4')

    # FORMATS TEXT TO BE PUT ON VIDEO
    font = cv2.FONT_HERSHEY_SIMPLEX
    coordinates = (150, 150)
    fontScale = 3
    color = (255, 0, 0)
    thickness = 2

    # SOURCE: https://www.geeksforgeeks.org/saving-a-video-using-opencv/
    size = (1910, 330)
    # VideoWriter object will create frames of the above size, store in output.mp4
    output_video = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 10, size)

    # LOOP THRU FRAMES OF VID AND ADD TEXT + CIRCLE
    i = 0 # overall frame count
    detected = 0 # counts the frames with circles in them
    # SOURCE: https://learnopencv.com/read-write-and-display-a-video-using-opencv-cpp-python/
    while input_video.isOpened():
        # capture frame by frame
        ret, frame = input_video.read()

        # crops frame as long as there are frames left
        try:
            # crops image [crop top, crop bottom, something, crop width]
            frame = frame[500:-250, 10:2000]
        except TypeError:
            pass

        # count frame
        i = i + 1
        if i > 56 and i < 373 and ret:
            frame, count = draw_circle(frame, i)
            detected = detected + int(count)

            # ADD TEXT
            display_text = "Frames Detected: " + str(detected) + "/467"
            frame = cv2.putText(frame, display_text, coordinates, font, fontScale, color, thickness, cv2.LINE_AA)

            # DISPLAY VID frame by frame
            cv2.imshow("Frame", frame)

            # press x to exit
            if cv2.waitKey(25) & 0xFF == ord('x'):
                break
        elif ret and (i <= 56 or i >= 373):
            # ADD TEXT
            display_text = "Frames Detected: " + str(detected) + "/467"
            frame = cv2.putText(frame, display_text, coordinates, font, fontScale, color, thickness, cv2.LINE_AA)

            # DISPLAY VID frame by frame
            cv2.imshow("Frame", frame)

            # press x to exit
            if cv2.waitKey(25) & 0xFF == ord('x'):
                break
        output_video.write(frame)
        if not ret:
            print("Detected: {}".format(detected))
            print("Total number of frames: {}".format(i - 1))
            break

    input_video.release()
    output_video.release()

from flask import Flask, request, render_template, send_file, Response
from robot import Robot
from time import sleep
import time
import picamera
import io
import sys
import logging

import cv2 as cv
import numpy as np
import math
import time

import queue
import threading

app = Flask('__name__')
rob = Robot()


# ------------------------- IMAGE PROCESSING FUNCTIONS -----------------------------
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def rotate(rotp: Point, transp: Point, angle):
    transp = Point(transp.x - rotp.x, transp.y - rotp.y)

    s = math.sin(angle)
    c = math.cos(angle)

    transp = Point(transp.x * c - transp.y * s, transp.x * s + transp.y * c)
    transp = Point(int(transp.x + rotp.x), int(transp.y + rotp.y))
    return transp


def distanceBetweenPoint2D(p1, p2):
    return math.sqrt(pow(p1.x - p2.x, 2) + pow(p1.y - p2.y, 2))


def lineSlope(p1, p2):
    diffX = p2.x - p1.x
    diffY = p2.y - p1.y
    if diffX == 0:
        return 100
    else:
        return diffY / diffX


class LineComponent:
    def __init__(self, p1, p2):
        self.centroid = Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
        self.length = distanceBetweenPoint2D(p1, p2)
        self.m = lineSlope(p1, p2)
        self.b = p1.y - self.m * p1.x
        self.p1 = p1
        self.p2 = p2
        if math.atan(self.m) < 0:
            self.angle = math.pi + math.atan(self.m)
        else:
            self.angle = math.atan(self.m)


def overlap(img, wcropped, tl, br):
    xoffset = tl[0]
    yoffset = tl[1]

    rs, cs, chs = wcropped.shape
    roi = img[yoffset:yoffset + rs, xoffset:xoffset + cs]
    ret, mask = cv.threshold(cv.cvtColor(wcropped, cv.COLOR_RGB2GRAY), 0, 255, cv.THRESH_BINARY)

    fg = cv.bitwise_and(wcropped, wcropped, mask)

    mask = cv.bitwise_not(mask)

    bg = cv.bitwise_or(roi, roi, mask=mask)

    finalroi = cv.add(bg, fg)

    wcropped = finalroi
    img[yoffset: yoffset + wcropped.shape[0], xoffset: xoffset + wcropped.shape[1]] = wcropped
    return img


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")

    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [2150, 0],
        [2150, 2500],
        [0, 2500]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv.getPerspectiveTransform(rect, dst)
    warped = cv.warpPerspective(image, M, (2000, 2000))

    # return the warped image
    return (warped, M)


def annotate(w):
    # file_bytes = np.asarray(bytearray(frame), dtype=np.uint8)
    # w = cv.imdecode(file_bytes, cv.IMREAD_COLOR)
    # cv.imwrite("testaaa.jpg", frame)
    # cv.imwrite("testaaa.jpg", frame)
    #     w = cv.resize(frame, (3024, 4032), interpolation=cv.INTER_AREA)

    # pt1 = (728, 1117)
    # pt2 = (2306, 1061)
    # pt3 = (2757, 3730)
    # pt4 = (261, 3762)
    # src_pts = np.array([pt1, pt2, pt3, pt4], dtype=np.float32)
    # w, matrix = four_point_transform(curve, src_pts)

    height = w.shape[0]
    width = w.shape[1]
    pts = np.array([[0, height / 2 - 90], [0, height / 2 - 40], [width, height / 2 - 40], [width, height / 2 - 90]])
    # img.shape[0] is height, img.shape[1] is width
    pts = order_points(pts)

    # oldangle = 0
    grayw = cv.cvtColor(w, cv.COLOR_BGR2GRAY)
    (thresh, im_bw) = cv.threshold(grayw, 128, 255, cv.THRESH_BINARY | cv.THRESH_OTSU)

    kernel = np.ones((5, 5), np.uint8)
    opening = cv.morphologyEx(im_bw, cv.MORPH_CLOSE, kernel)

    # (1) Crop the bounding rect
    rect = cv.boundingRect(pts)
    x, y, wi, h = rect
    croped = opening[y:y + h, x:x + wi].copy()

    rect = cv.boundingRect(pts)
    x, y, wi, h = rect
    croped2 = w[y:y + h, x:x + wi].copy()

    # cv.imshow("", croped)
    # cv.waitKey(0)

    #     ## (2) make mask
    #     pts = pts - pts.min(axis=0)

    #     mask = np.zeros(croped.shape[:2], np.uint8)
    #     cv.drawContours(mask, [pts], -1, (255, 255, 255), -1, cv.LINE_AA)

    #     ## (3) do bit-op
    #     dst = cv.bitwise_and(croped, croped, mask=mask)
    #     # 3024 40

    #     ## (4) add the white background
    #     bg = np.ones_like(croped, np.uint8) * 255
    #     cv.bitwise_not(bg, bg, mask=mask)
    #     dst2 = bg + dst

    #     edges = cv.Canny(dst2, 0, 255)
    edges = cv.Canny(croped, 0, 255)

    linesP = cv.HoughLinesP(edges, rho=4, theta=np.pi / 180, threshold=20, minLineLength=20, maxLineGap=50)

    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv.line(croped2, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 3, cv.LINE_AA)
    # cv.imwrite("testaaa.jpg", croped2)

    lineComponents = []
    if linesP is not None:
        for l in linesP:
            templine = LineComponent(Point(l[0][0], l[0][1]), Point(l[0][2], l[0][3]))
            # if not (templine.m > -0.5 and templine.m < 0.5):
            lineComponents.append(templine)

    lineComponents = sorted(lineComponents, key=lambda l: l.length, reverse=True)

    if len(lineComponents) < 4:
        newframe = cv.imencode('.jpeg', w)[1]
        return (newframe, False, 0)

    leftMost = []
    rightMost = []
    leftMost.append(lineComponents[0])
    tempComp = leftMost[0]
    index = 0
    # if linesP is not None:
    #     for i in range(0, len(linesP)):
    #         = linesP[i][0]

    for l in lineComponents[1:]:
        d = distanceBetweenPoint2D(tempComp.centroid, l.centroid)
        if d > 300:
            if index == 0 and len(rightMost) < 2:
                rightMost.append(l)
                index = 1
                tempComp = l
            elif index == 1 and len(leftMost) < 2:
                leftMost.append(l)
                index = 0
                tempComp = l
        else:
            if index == 0 and len(leftMost) < 2:
                leftMost.append(l)
                tempComp = l
            elif index == 1 and len(rightMost) < 2:
                rightMost.append(l)
                tempComp = l
        if len(leftMost) >= 2 and len(rightMost) >= 2:
            break
    if len(leftMost) < 2 or len(rightMost) < 2:
        if len(leftMost) < 1 or len(rightMost) < 1:
            newframe = cv.imencode('.jpeg', w)[1]
            return (newframe, True, 0)
        else:
            for l in leftMost:
                cv.line(w, (l.p1.x, int(height / 2 - 90 + l.p1.y)), (l.p2.x, int(height / 2 - 90 + l.p2.y)),
                        (0, 255, 0),
                        2)
            for l in rightMost:
                cv.line(w, (l.p1.x, int(height / 2 - 90 + l.p1.y)), (l.p2.x, int(height / 2 - 90 + l.p2.y)),
                        (0, 255, 0),
                        2)
            for l in lineComponents[1:]:
                d = distanceBetweenPoint2D(tempComp.centroid, l.centroid)
                if d > 200:
                    if len(rightMost) < 1:
                        rightMost.append(l)
                        break
            px = (leftMost[0].centroid.x + rightMost[0].centroid.x) / 2
            py = (leftMost[0].centroid.y + rightMost[0].centroid.y) / 2
            pangle = (leftMost[0].angle + rightMost[0].angle) / 2
            pm = math.tan(pangle)



    else:
        for l in leftMost:
            cv.line(w, (l.p1.x, int(height / 2 - 100 + l.p1.y)), (l.p2.x, int(height / 2 - 100 + l.p2.y)), (0, 255, 0),
                    2)
        for l in rightMost:
            cv.line(w, (l.p1.x, int(height / 2 - 100 + l.p1.y)), (l.p2.x, int(height / 2 - 100 + l.p2.y)), (0, 255, 0),
                    2)

        px = (leftMost[0].centroid.x + leftMost[1].centroid.x + rightMost[0].centroid.x + rightMost[
            1].centroid.x) / 4
        py = (leftMost[0].centroid.y + leftMost[1].centroid.y + rightMost[0].centroid.y + rightMost[
            1].centroid.y) / 4

        pangle = (leftMost[0].angle + leftMost[1].angle + rightMost[0].angle + rightMost[1].angle) / 4
        pm = math.tan(pangle)

    # print((leftMost[0].m, leftMost[1].m, rightMost[0].m, rightMost[1].m))

    # px = (leftMost[0].centroid.x + rightMost[0].centroid.x) / 2
    # py = (leftMost[0].centroid.y + rightMost[0].centroid.y) / 2
    #
    # pm = (leftMost[0].m + rightMost[0].m) / 2
    if pm == 0:
        bottomx = 10000
    else:
        bottomx = int(180 / pm + px)
    bottomy = int(py + 180)
    cv.arrowedLine(w, (bottomx + x, bottomy + y), (int(px) + x, int(py) + y), (255, 0, 0), 3, cv.LINE_AA)

    # convert type back
    newframe = cv.imencode('.jpeg', w)[1]

    return (newframe, True, pangle)


# ------------------------- CAMERA STREAM -------------------------------
inq = queue.LifoQueue()
outq = queue.LifoQueue()


def generate():
    stream1 = cv.VideoCapture(0)
    stream1.set(cv.CAP_PROP_FPS, 5)
    while stream1.isOpened():
        ret, frame = stream1.read()
        frame = cv.rotate(frame, cv.ROTATE_180)
        # lock.acquire()
        # try:
        inq.put(frame)
        # finally:
        #     lock.release()
        if ret:
            frame = cv.imencode('.jpeg', frame)[1]
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')


def gen_edited():
    while True:
        # with lock:
        frame = inq.get()
        newframe, irrelevantboolean, angle = annotate(frame)
        # with outlock:
        outq.put(angle)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + newframe.tobytes() + b'\r\n')


@app.route('/stream')
def stream():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route('/edited')
def edited():
    # get image from processed Q
    # outq.get()
    return Response(gen_edited(), mimetype="multipart/x-mixed-replace; boundary=frame")


# ---------------------------- LOG STREAM -------------------------------
class NoParsingFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().__contains__('logstream')


@app.route('/entirelog')
def entirelog():
    with open("logfile.log", "r") as file:
        return "".join(file.readlines()[-10:])


@app.route('/logstream')
def logstream():
    output = ""
    with open("logfile.log", "r") as file:
        lines = file.readlines()
        for i in range(len(lines) - 4, len(lines)):
            output = output + lines[i] + "<br>"

    return Response(output)


# ------------------------- HTML TEMPLATE -------------------------------
@app.route('/ui')
def index():
    return render_template('index.html')


# ------------------------- ROBOT MOTIONS -------------------------------
# AUTOMATICALLY RUNS MAZE
@app.route('/run')
def auto():
    # i = 0
    while True:
        # if i == 1:
        #     rob.move_forward(1)
        #     rob.turn_left(90)
        angle = outq.get()
        if angle == 0:
            continue
        # if math.tan(angle) < 1.5:
        #     i = 1
        rob.move_forward(1)
        time.sleep(0.1)
        if angle < math.pi / 2:
            angle = angle * 180 / math.pi
            print("angle: " + str((90 - angle)))
            rob.turn_left((90 - angle)/2)
        # elif angle == math.pi/2:
        #     rob.move_forward(1)
        else:
            angle = 180 - angle * 180 / math.pi
            print("angle: " + str((90 - angle)))
            rob.turn_right((90 - angle)/2)

        time.sleep(0.1)

    return "you will find your way out of any maze!! :)))"


# FORWARD FUNCTION
# call this from your browser using http://192.168.1.243:7777/fwd?f=1
@app.route('/fwd', methods=['GET'])
def rest_fwd():
    # args is to retrieve GET data (from query strings, which is whatever foll$
    f_dist = request.args.get('d', default=1, type=float)
    rob.move_forward(f_dist)
    return "always moooove forward!! :))))"


# BACKWARD FUNCTION
@app.route('/bwd', methods=['GET'])
def rest_bwd():
    b_dist = request.args.get('d', default=1, type=int)
    rob.move_backward(b_dist)
    return "it's okay to take a step back and relax!! #selfcare :)))"


# TURN LEFT FUNCTION
# call this from your browser using http://192.168.1.243:7777/fwd?l=1
@app.route('/left', methods=['GET'])
def rest_left():
    l_deg = request.args.get('a', default=90, type=float)
    rob.turn_left(l_deg)
    return "we'll never left you behind <3333333333333"


# TURN RIGHT FUNCTION
@app.route('/right', methods=['GET'])
def rest_right():
    r_deg = request.args.get('a', default=90, type=float)
    rob.turn_right(r_deg)
    return "you are always right. :)))))))"


@app.route('/stop', methods=['GET'])
def stop_rob():
    rob.stop()
    del rob
    return 200


# ------------------------- MAIN -------------------------------
if __name__ == "__main__":
    # log(__name__)

    file_handler = logging.FileHandler("logfile.log")
    file_handler.addFilter(NoParsingFilter())
    logging.basicConfig(filename="logfile.log", level=logging.INFO)
    logging.info("Starting App")  # this adds your message into log, can also use debug, warning, etc
    # threading.Thread(target = generate).start()
    threading.Thread(target=gen_edited).start()
    app.run(host='0.0.0.0', port=7777, debug=True)

from flask import Flask, request, render_template, send_file, Response
from robot import Robot
from time import sleep
import time
import picamera
import io
import sys
import logging


app = Flask('__name__')
rob = Robot()

# ------------------------- CAMERA STREAM -------------------------------
def generate():
    # Create an in-memory stream
    my_stream = io.BytesIO()

    while True:
        with picamera.PiCamera() as camera:
            camera.start_preview()
            camera.framerate = 49
            camera.exposure_mode = 'sports'
            camera.rotation = 180
            camera.capture(my_stream, 'jpeg', use_video_port=True)
            my_stream.seek(0)
            frame = my_stream.read()
            my_stream.seek(0)
            my_stream.flush()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/stream')
def stream():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


# ---------------------------- LOG STREAM -------------------------------
class NoParsingFilter(logging.Filter):
    def filter(self, record):
        return not record.getMessage().__contains__('logstream')

@app.route('entirelog')
def entirelog():
    with open("logfile.log", "r") as file:
        return "".join(file.readlines()[-10:])

@app.route('/logstream')
def logstream():
    output = ""
    with open("logfile.log", "r") as file:
        lines = file.readlines()
        for i in range(len(lines)-4, len(lines)):
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
    rob.run()
    return "you will find your way out of any maze!! :)))"


# FORWARD FUNCTION
# call this from your browser using http://192.168.1.243:7777/fwd?f=1
@app.route('/fwd', methods=['GET'])
def rest_fwd():
    # args is to retrieve GET data (from query strings, which is whatever foll$
    f_dist = request.args.get('d', default=1, type=int)
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
    l_deg = request.args.get('a', default=90, type=int)
    rob.turn_left(l_deg)
    return "we'll never left you behind <3333333333333"


# TURN RIGHT FUNCTION
@app.route('/right', methods=['GET'])
def rest_right():
    r_deg = request.args.get('a', default=90, type=int)
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
    app.run(host='0.0.0.0', port=7777, debug=True)

from flask import Flask, request
from robot import Robot

app = Flask('__name__')
rob = Robot()

# AUTOMATICALLY RUNS MAZE
@app.route('/run')
def auto():
    rob.run()
    return "you will find your way out of any maze!! :)))"


# FORWARD FUNCTION
# call this from your browser using http://192.168.1.243:7777/fwd?d=1
@app.route('/fwd', methods=['GET'])
def rest_fwd():
    # args is to retrieve GET data (from query strings, which is whatever follows the question mark)
    f_dist = request.args.get('d', default=1, type=float)
    rob.move_forward(f_dist)
    return "always moooove forward!! :))))"


# BACKWARD FUNCTION
@app.route('/bwd', methods=['GET'])
def rest_bwd():
    b_dist = request.args.get('d', default=1, type=float)
    rob.move_backward(b_dist)
    return "it's okay to take a step back and relax!! #selfcare :)))"


# TURN LEFT FUNCTION
# call this from your browser using http://192.168.1.243:7777/left?a=1
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7777, debug=True)

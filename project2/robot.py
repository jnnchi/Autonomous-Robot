import RPi.GPIO as GPIO
import time
from motor import Motor

"""
enableL = 13
backwardL = 33
forwardL = 32

enableR = 11
backwardR = 12
forwardR = 35
"""

class Robot(Motor):
  def __init__(self):
    Motor.__init__(self, 13, 12,32,11,33,35)
  
  # here we stop the robot between each function call to hopefully stabilize it better
  def run(self):
    self.move_forward(4)
    self.stop()
    self.turn_right(90)
    self.stop()
    self.move_forward(4.9)
    self.stop()
    self.move_backward(0.5)
    self.stop()
    self.turn_right(90)
    self.stop()
    self.move_forward(4.2)
    self.stop()
    del self

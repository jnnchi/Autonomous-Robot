# CODE WRITTEN IN OCTOBER OF 2021

import RPi.GPIO as GPIO
import time
from motor import Motor

"""
enableL = 13
backwardL = 12
forwardL = 32
enableR = 11
backwardR = 33
forwardR = 35
"""

class Robot(Motor):
  def __init__(self):
    Motor.__init__(self, 13, 12,32,11,33,35)

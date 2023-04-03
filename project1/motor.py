# CODE WRITTEN IN OCTOBER 2021

import RPi.GPIO as GPIO
import time

class Motor():
    def __init__(self, enableL, backwardL, forwardL, enableR, backwardR, forwardR):
        self.__enableL = enableL
        self.__backwardL = backwardL
        self.__forwardL = forwardL
        self.__enableR = enableR
        self.__backwardR = backwardR
        self.__forwardR = forwardR

        self.__pin_list = [self.__enableL, self.__backwardL, self.__forwardL, self.__enableR, self.__backwardR,
                           self.__forwardR]

        # will specify pins by pin number
        GPIO.setmode(GPIO.BOARD)

        # initialize GPIO pins
        for pin_num in self.__pin_list:
            GPIO.setup(pin_num, GPIO.OUT)
            GPIO.output(pin_num, GPIO.HIGH)
            
        # sets constant conversion factor
        self.__MOTOR_CF = 0.97

        # set PWM; turns on motors
        self.__enableL_pwm = GPIO.PWM(self.__enableL, 10)
        self.__enableR_pwm = GPIO.PWM(self.__enableR, 10)
        time.sleep(1)

    # destructor resets all pins
    def __del__(self):
        GPIO.cleanup()
        
    # new forward function, with distance (in feet) as a parameter
    def move_forward(self, distance):
        # setting output (go forward but not backward)
        GPIO.output(self.__forwardL, True)
        GPIO.output(self.__backwardL, False)
        GPIO.output(self.__forwardR, True)
        GPIO.output(self.__backwardR, False)

        # tell enabler pins to start PWM
        self.__enableL_pwm.start(20 * self.__MOTOR_CF)
        self.__enableR_pwm.start(20)
        
        # 1.09 is the determined amount of time needed to move forward by the length of the robot
        time.sleep(0.95 * distance + 1)

    # set all pin output to 0
    def stop(self):
        for pin_num in self.__pin_list:
            GPIO.output(pin_num, 0)
        time.sleep(1)

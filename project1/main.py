# CODE WRITTEN IN OCTOBER OF 2021

from motor import Motor
from robot import Robot

if __name__ == "__main__":
    rob = Robot()
    rob.move_forward(1) # move forward a distance of 1 foot
    rob.stop()
    del rob

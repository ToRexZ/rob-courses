

from math import sqrt, acos
from controller import Supervisor, Motor, Node, Field, Compass, Robot
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

robot = Supervisor()
timestep = int(robot.getBasicTimeStep())
print(timestep)


# Compass
compass = Compass("compass")
if compass is None:
    print("Could not find a compass.")
    exit()
compass.enable(100)


# MOTORS
# Find motors and set them up to velocity control
left_motor = Motor("wheel_left_joint")
right_motor = Motor("wheel_right_joint")

if left_motor is None or right_motor is None:
    print("Could not find motors.")
    exit()
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))

heading_init=robot.getSelf().getOrientation() #initial heading
pose_init=robot.getSelf().getPosition() #initial position
print(f"initial heading: {heading_init}")
print(f"initial position {pose_init}")


pose_init[0:2]=np.array([1,2])


pose_h=np.zeros((2,4))
pose_h[0:,0]=pose_init[0:2]



print(f"pose_h: {pose_h}")




i = 0
while robot.step(timestep) != -1 and i<100:

  i+=1
  pass
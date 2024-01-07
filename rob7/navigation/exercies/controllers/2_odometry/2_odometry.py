"""3_odometry controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot, Supervisor, Motor, Compass, Lidar 


import matplotlib.pyplot as plt
import math
import copy
import numpy as np

# Plt settings
plt.xlim(-10, 10)
plt.ylim(-10, 10)




supervisor = Supervisor()


robot = Robot()

# parameters of the robot:
wheel_base = 0.20225*2
wheel_radius = 0.0985
current_position = [0, 0, 0]




timestep = int(supervisor.getBasicTimeStep())
# timesteps in seconds
timestep_s = timestep / 1000

lidar = Lidar("lidar")
lidar.enable(timestep)



# Compass
compass = Compass("compass")
if compass is None:
    print("Could not find a compass.")
    exit()

compass.enable(timestep)





# MOTORS
# Find motors and set them up to velocity control
left_motor = Motor("wheel_left_joint")
right_motor = Motor("wheel_right_joint")



if left_motor is None or right_motor is None:
    print("Could not find motors.")
    exit()

left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))

# Encoders
left_encoder = supervisor.getDevice("wheel_left_joint_sensor")
right_encoder = supervisor.getDevice("wheel_right_joint_sensor")
if left_encoder is None or right_encoder is None:
    print("Could not find encoders.")
    exit()

left_encoder.enable(timestep)
right_encoder.enable(timestep)


# Exercise 1: Function that plots lidar coordinates dynamicly in cartesian space using matplotlib
def plot_lidar(x, y):
    plt.scatter(x, y)

def plot_odometry(x, y, yaw):
  plt.arrow(x, y, 0.5*math.cos(yaw), 0.5*math.sin(yaw), head_width=0.2, head_length=0.1, fc='k', ec='k')


# Convert lidar ranges to cartesian coordinates in the robot frame
def convert_to_cartesian(lidar_ranges, fov, robot_pose):
    x = []
    y = []

    angle_step = fov / len(lidar_ranges)

    robot_x = robot_pose[0]
    robot_y = robot_pose[1]
    robot_yaw = robot_pose[2]

    # Lidar points go from left to right
    lidar_start_angle = fov / 2

    angle_step = fov / len(lidar_ranges)

    for i in range(len(lidar_ranges)):
        angle = robot_yaw + lidar_start_angle - (i * angle_step)
        x.append(robot_x + lidar_ranges[i] * math.cos(angle))
        y.append(robot_y + lidar_ranges[i] * math.sin(angle))

    return x, y




# update odometry
def update_odometry(current_position, timestep, left_wheel_vel, right_wheel_vel, wheel_base, wheel_radius):
    new_position = []


    # Compute linear and angular velocity
    linear_velocity = wheel_radius * (left_wheel_vel + right_wheel_vel) / 2
    angular_velocity = wheel_radius * (right_wheel_vel - left_wheel_vel) / wheel_base


   # Compute new position and orientation
    new_position.append(current_position[0] + linear_velocity * timestep_s * math.cos(current_position[2]))
    new_position.append(current_position[1] + linear_velocity * timestep_s * math.sin(current_position[2]))
    new_position.append(current_position[2] + angular_velocity * timestep_s)

    return new_position
    
def get_velocities(previous_endcoder_values):
  encoder_values = np.zeros(2)
  velocities = np.zeros(2)

  # Get encoder values
  encoder_values[0] = left_motor.getVelocity()

  encoder_values[0] = left_encoder.getValue()
  encoder_values[1] = right_encoder.getValue()

  # Compute the wheel differences
  left_diff = encoder_values[0] - previous_endcoder_values[0]
  right_diff = encoder_values[1] - previous_endcoder_values[1]

  # Incorporate the timedifference
  velocities[0] = left_diff / timestep_s 
  velocities[1] = right_diff / timestep_s

  return velocities, encoder_values
  


odom_path = []
ground_truth_path = []

def update_path(new_position):
  odom_path.append(new_position)

# Plot the path as lines
def plot_path(path, color='r', label='path'):
  x = []
  y = []

  for i in range(len(path)):
    x.append(path[i][0])
    y.append(path[i][1])

  plt.plot(x, y, color=color, label=label)


# Function to convert quaternion to euler angles
def quat_to_eul(quatertion):
    x = quatertion[0]
    y = quatertion[1]
    z = quatertion[2]
    w = quatertion[3]

    roll = math.atan2(2*(w*x + y*z), 1 - 2*(x**2 + y**2))
    pitch = math.asin(2*(w*y - z*x))
    yaw = math.atan2(2*(w*z + x*y), 1 - 2*(y**2 + z**2))

    return roll, pitch, yaw



# Wheel velocities
wheel_velocities = [3.0, 1.5]
wheel_velocity_noise = 1.0

left_motor.setVelocity(wheel_velocities[0] + np.random.normal(0, wheel_velocity_noise))
right_motor.setVelocity(wheel_velocities[1] + np.random.normal(0, wheel_velocity_noise))

prev_encoder_values = np.zeros(2)


counter = 0

while supervisor.step(timestep) != -1:
    # Set wheel velocities
    if counter > 100:
      left_motor.setVelocity(wheel_velocities[0] + np.random.normal(0, wheel_velocity_noise))
      right_motor.setVelocity(wheel_velocities[1] + np.random.normal(0, wheel_velocity_noise))
      counter = 0
    counter+=1


    # measured velocities based on encoders:
    measured_wheel_velocities, prev_encoder_values = get_velocities(prev_encoder_values)

    new_position = update_odometry(current_position, timestep, measured_wheel_velocities[0], measured_wheel_velocities[1], wheel_base, wheel_radius)

    update_path(new_position)

    current_position = copy.deepcopy(new_position)

    lidar_points = lidar.getRangeImage()
    lidar_fov = lidar.getFov()
    x,y = convert_to_cartesian(lidar_points, lidar_fov, current_position)
    plot_lidar(x, y)
    plot_odometry(current_position[0], current_position[1], current_position[2])
    plot_path(odom_path, label="Odometry path")

    # Ground truth
    ground_truth_position = supervisor.getFromDef("robot").getField("translation").getSFVec3f()
    ground_truth_orientation = quat_to_eul(supervisor.getFromDef("robot").getField("rotation").getSFRotation())[2]
    ground_truth_path.append([ground_truth_position[0],ground_truth_position[1], ground_truth_orientation])
    plot_path(ground_truth_path, color='b', label="Ground truth path")



    plt.legend()
    plt.axis('equal')
    plt.xlim(-6, 6)
    plt.ylim(-6, 6)
    plt.pause(0.0001)
    plt.clf()

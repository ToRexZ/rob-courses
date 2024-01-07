"""TIAGo_Base controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot, Supervisor, Compass, Motor, Node, LidarPoint, Lidar, Gyro, Accelerometer
import matplotlib.pyplot as plt
import math 
import numpy as np

# create the Robot instance.
supervisor = Supervisor()
robot = supervisor.getFromDef("robot")


# Devices:
leftMotor = Motor("wheel_left_joint")
rightMotor = Motor("wheel_right_joint")

leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))

leftMotor.setVelocity(0)
rightMotor.setVelocity(0)

# Lidar
lidar = Lidar("lidar")
lidar.enable(100)

# get the time step of the current world.
timestep = int(supervisor.getBasicTimeStep())

dt = timestep / 1000


# Compass
compass = Compass("compass")
if compass is None:
    print("could not find compass")
    exit()

compass.enable(timestep)

# Gyro
gyro = Gyro("gyro")
if gyro is None: 
    print("could not find gyro")
    exit()
gyro.enable(timestep)

# Accelerometer
accelerometer = Accelerometer("accelerometer")
if accelerometer is None:
    print("could not find accelerometer")
    exit()
accelerometer.enable(timestep)


def getCompassAngle(radians=True):
    measuredValues = compass.getValues()
    radians = math.atan2(measuredValues[1], measuredValues[0])

    # Rotate direction of north to be along the x axis
    bearing = radians - math.pi/2 

    # Add noise to the compass
    bearing += true_compass_offset + np.random.randn(1) * 0.02 

    if bearing < 0:
      bearing += 2 * math.pi


    return 2*math.pi - bearing[0] 

def get_gyro_velocity():
  # Get measurements of the gyro
  # The values are velocity measurements around each axis in rad/s
  gyro_measurements = gyro.getValues()

  omega = gyro_measurements[2]

  # Add noise 
  # Add noise to the compass
  omega += true_gyro_offset + np.random.randn(1) * 0.02 

  return omega[0]

def robot_heading():
  # Get the true rotation of the robot
  rotation = robot.getOrientation()
  true_angle = convert_to_yaw(rotation)
  return true_angle


angle_differences = []

# Calibrate the compass
def calibrateCompass():
  # Could calibrate the compass by using the known initial angle of the robot and that north is directly along the y axis of the robot, thus the angle could 
  
  
  compass_angle = getCompassAngle()

  true_angle = robot_heading()

  angle_difference = compass_angle - true_angle
  angle_differences.append(angle_difference)

  plt.arrow(0, 0, math.cos(compass_angle), math.sin(compass_angle), color='r', width=0.1, label="Compass")
  plt.arrow(0, 0, math.cos(true_angle), math.sin(true_angle), color='g', width=0.1, label="True Angle")




omega_differences = []

# Calibrate the gyro
def calibrateGyro(prev_angle):
  measured_velocity =  get_gyro_velocity()

  # Get the true rotation of the robot
  true_angle = robot_heading()
  
  # Compute the angular velocity of the robot in rad/s
  omega = (true_angle - prev_angle) / dt

  print(f"measured_velocity: {measured_velocity}")
  print(f"omega: {omega}")

  omega_difference =  omega - measured_velocity
  omega_differences.append(omega_difference)

  plt.arrow(2, 0, math.cos(omega), math.sin(omega), color='b', width=0.1, label="True Omega")
  plt.arrow(2, 0, math.cos(measured_velocity), math.sin(measured_velocity), color='c', width=0.1, label="Measured Omega")

  return true_angle








def calibrateAccelerometer():
  # Get measurements of the accelerometer
  accelerometer_measurements = accelerometer.getValues()



    

def quat_to_eul(quatertion):
    x = quatertion[0]
    y = quatertion[1]
    z = quatertion[2]
    w = quatertion[3]

    roll = math.atan2(2*(w*x + y*z), 1 - 2*(x**2 + y**2))
    pitch = math.asin(2*(w*y - z*x))
    yaw = math.atan2(2*(w*z + x*y), 1 - 2*(y**2 + z**2)) 

    return yaw

# Convert 3D rotational matrix to yaw angle
# This is the rotation matrix. 
# [ R[0] R[1] R[2] ]
# [ R[3] R[4] R[5] ]
# [ R[6] R[7] R[8] ]
def convert_to_yaw(rotation_matrix):
    R = rotation_matrix
    yaw = math.atan2(R[1], R[0]) * -1
    if yaw < 0:
        yaw += 2 * math.pi
    return yaw


fig, ax = plt.subplots()

plt.xlim(-5, 5)
plt.ylim(-5, 5)
plt.axis('equal')


plt.ion()

leftMotor.setVelocity(-1)
rightMotor.setVelocity(1)


# Define actual offset for the compass
true_compass_offset = 0.5
true_gyro_offset = 0.5


last_true_angle = 0

# Main loop:
while supervisor.step(timestep) != -1 and len(angle_differences) < 500:

    plt.xlim(-5, 5)
    plt.ylim(-5, 5)
    
    # Calibrate the compass
    calibrateCompass()

    # Calibrate the gyro
    last_true_angle = calibrateGyro(last_true_angle)

    # Calibrate the accelerometer
    calibrateAccelerometer()



    plt.legend()
    plt.grid(True)
    plt.pause(0.0001)
    plt.cla()


# Compute compass offset
compass_offset = np.mean(angle_differences)
print(f"compass_offset: {compass_offset}")

# Compute gyro offset
print(f"omega_differences: {omega_differences}")

# Remove outliers that occur at wrap around
omega_differences = [x for x in omega_differences if x < math.pi and x > - math.pi]

mean_omega_difference = np.mean(omega_differences)
print(f"mean_omega_difference: {mean_omega_difference}")

print(f"min omega_differences: {np.min(omega_differences)}")
print(f"max omega_differences: {np.max(omega_differences)}")


while supervisor.step(timestep) != -1:
    plt.xlim(-5, 5)
    plt.ylim(-5, 5)

    # Plot the corrected compass
    compass_angle = getCompassAngle() + compass_offset
    rotation = robot.getOrientation()
    true_angle = convert_to_yaw(rotation)
    plt.arrow(0, 0, math.cos(compass_angle), math.sin(compass_angle), color='r', width=0.1, label="Calibrated Compass")
    plt.arrow(0, 0, math.cos(true_angle), math.sin(true_angle), color='g', width=0.1, label="True Angle")

    # Plot the corrected gyro
    corrected_gyro = get_gyro_velocity() + mean_omega_difference
    omega = (true_angle - last_true_angle) / dt
    last_true_angle = true_angle
    plt.arrow(2, 0, math.cos(omega), math.sin(omega), color='b', width=0.1, label="True Omega")
    plt.arrow(2, 0, math.cos(corrected_gyro), math.sin(corrected_gyro), color='c', width=0.1, label="Corrected measured Omega")


    # plot the corrected accelerometer


    plt.legend()
    plt.grid(True)
    plt.pause(0.0001)
    plt.cla()

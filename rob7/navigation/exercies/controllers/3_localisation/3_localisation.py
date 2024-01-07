"""bug1 controller."""

from math import sqrt, acos
import math
from controller import Supervisor, Motor, Node, Field, Compass, Robot
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

robot = Robot()
supervisor = Supervisor()
timestep = int(robot.getBasicTimeStep())


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


# If True, example code will run. If False, you can run my own code.
test = True


if not test:

  print("Start")
  fig, ax = plt.subplots()  # Create a figure containing a single axes.
  Xdata = np.zeros(1000)
  Ydata = np.zeros(1000)
  # Position measurement. --- h is the measurement function
  pose_h=np.zeros((2,1000))
  heading_h=np.zeros((2,1000))
  heading_h[0:,0]=1  # Set the first column to 1, both rows
  print(f"hh: {heading_h}")

  heading_init=robot.getSelf().getOrientation() #initial heading
  pose_init=robot.getSelf().getPosition() #initial position
  print(f"h_init{heading_init}")
  print(f"x_init{pose_init}")
  print(f"x_init[0:2]{pose_init[0:2]}")
  pose_h[0:,0]=pose_init[0:2] #store initial position in all rows of xh
  heading_h[0,0]=heading_init[0]
  heading_h[1,0]=heading_init[3]
  print(f"xh[0:,0]{pose_h[0:,0]}")
  print(f"hh[0:,0]{heading_h[0:,0]}")
  R = np.array([[0, -1], [1, 0]])  #90 deg rotation matrix
  h1=[1,0] 
  #print(np.sin(1.94))
  print(f"hh[0:,0]: {heading_h[0:,0]}")
  heading_h[0:,1]=np.matmul(R,heading_h[0:,0]) # set next heading to 90 deg rotation of initial heading
  print(f"heading_h[0:,1]: {heading_h[0:,1]}")
  i=0

  D=0.20225*2 # Tiago width
  rw=0.0985 #Tiago wheel radius
  #at wheel speeds 1.0 and 1.0 Tiago seems to move 0.633 m pr 100 steps
  #this means that forward speed is 0.633(wa+wb)/2/100 pr step
  #at wheel speeds 1.0 and -1.0 Tiago seems to move 2.58 rad m pr 100 steps
  #this means that angular velocity is 2.58(wa-wb)/2/100 rad pr step 
  wa=1
  wb=0.5
  #feature positions
  B=np.array([[0, 1, 0, -1],[0, 1, 2, 1]])

  # Plot some data on the axes.
  while robot.step(timestep) != -1 and i<999:
      left_motor.setVelocity(wa)
      right_motor.setVelocity(wb)

      # Compute the linear velocity
      ws=0.633*(wa+wb)/2/100 
      # Compute the angular velocity
      wd=2.58*(wb-wa)/2/100 #angular velocity
      
      # ----------------------------------------
      # This is the Action update:
      # Next position is current position plus distance travelled in current heading
      pose_h[0:,i+1]=np.add(pose_h[0:,i] , np.multiply(heading_h[0:,i],ws)) #update position

      # Next heading is the current heading plus the rotation
      heading_h[0:,i+1]=np.add(heading_h[0:,i],np.multiply(np.matmul(R,heading_h[0:,i]),wd)) #update heading
      # ----------------------------------------

      Bd=np.subtract(B[0:,0],pose_h[0:,i+1]) #vector from Tiago to feature, in this case to the origin.
      # print(np.vdot(Bd, heading_h[0:,i]))
      #print(compass.getValues())
      #CGV = compass.getValues()
      #print(CGV[0])
      #print(Xdata[i])
      #Xdata[i]=CGV[0]
      #Ydata[i]=CGV[1]
      i=i+1
  
  left_motor.setVelocity(0.0)
  right_motor.setVelocity(0.0)   
      
  ax.plot(pose_h[0,0:], pose_h[1,0:],'bo')  
  plt.show()



else: 
  # Exercise 2: Implement the particle filter to your odometry solution in webots

  # Particle filter parameters:
  num_particles = 100 
  
  # Generate n random particles uniformly distributed in the map
  import random
  particles = np.array([(random.uniform(-5, 5), random.uniform(-5,5), random.uniform(0, 2*np.pi)) for _ in range(num_particles)])



  # Motion noise
  motion_noise = 0.01

  # Sensor/measurement noise
  sensor_noise = 0.05


  # Obstacles used to measure against
  obstacles = np.array([[0,-1],[2, 3],[-1, 4],[-3, 4],[3, 3],[4, -3], [-1, -4], [-5, -4], [3, -3]])

  # parameters of the robot:
  wheel_base = 0.20225*2
  wheel_radius = 0.0985


  # Update odometry based on velocity commands and time steps
  def update_odometry(current_position, timestep, left_wheel_vel, right_wheel_vel, wheel_base, wheel_radius, noise):
      new_position = []

      # timesteps in seconds
      timestep_s = timestep / 1000

      # Compute linear and angular velocity
      linear_velocity = wheel_radius * (left_wheel_vel + right_wheel_vel) / 2
      angular_velocity = wheel_radius * (right_wheel_vel - left_wheel_vel) / wheel_base

      # Noise for each state
      noise_array = np.array([0, 0, 0])
      
      # Sample the noise for each state from a normal distribution with 0 mean
      for i in range(len(noise_array)):
        noise_array[i] = np.random.normal(0, noise)

    # Compute new position and orientation
      new_position.append(current_position[0] + linear_velocity * timestep_s * math.cos(current_position[2]) + noise_array[0]) 
      new_position.append(current_position[1] + linear_velocity * timestep_s * math.sin(current_position[2]) + noise_array[1])
      new_position.append(current_position[2] + angular_velocity * timestep_s + noise_array[2])

      return new_position
      

  def distance_to_obstacle(particle, obstacle):
    return np.linalg.norm(particle[:2] - obstacle)


  def predicted_sensor_data(particles, obstacles):
    # Compute the distance from each particle to the obstacle
    distances = np.zeros((len(obstacles), len(particles)))
    for i, particle in enumerate(particles):
      for j, obstacle in enumerate(obstacles):
        distances[j][i] = np.linalg.norm(particle[:2] - obstacle)
    
    return distances
  


  def observation_sensor_data(obstacles, noise):
    # Get actual robot position and orientation, used only to get sensor data
    position = supervisor.getFromDef("robot").getField("translation").getSFVec3f()

    # Compute the distance from the robot to the obstacle
    distances = np.zeros(len(obstacles))
    for j, obstacle in enumerate(obstacles):
      distances[j] = np.linalg.norm(obstacle - position[:2])



    # Add noise to the measurements
    distances += np.random.normal(0, noise, distances.shape)

    return distances


  def compute_weights(observations, predicted_distances, noise):
    # Comptue likelihood of each particle based on the observation based on a gaussian distribution
    def measurement_likelihood(observation, predicted_distance, noise):
      likelihood = 1.0 / np.sqrt(2 * np.pi * noise**2)
      likelihood *= np.exp(-(observation - predicted_distance)**2 / (2 * noise*2))
      return likelihood

    # An array to store the weights of each particle
    weights = np.zeros(np.shape(predicted_distances)[1])


    # Itterate through all particles
    for i in range(len(predicted_distances[0])):
      for j in range(len(predicted_distances)):
        # Compute the likelihood of each distance for each particle. Since there is 10 distances and 100 particles, we get a 10x100 matrix
        likelihoods = [measurement_likelihood(obs, predicted_distances[j][i], noise) for obs in observations]
        weights[i] = np.prod(likelihoods)
    
  
    
    # for i, particle_distance in enumerate(predicted_distances):
    #   print(i)
    #   # Compute the likelihood of each distance for each particle. Since there is 10 distances and 100 particles, we get a 10x100 matrix
    #   print(f"Particle distance: {particle_distance}, shape: {particle_distance.shape}")
    #   print(f"Observation: {observations[0]}")
    #   likelihoods = [measurement_likelihood(obs, particle_distance, sensor_noise) for obs in observations]
    #   weights[i] = np.prod(likelihoods)

    # Normalize the weights
    weights /= np.sum(weights)

    return weights





    


  def resample(particles, weights, noise_std=0.01):
    # Sample the particles based on the weights
    particle_indices = np.random.choice(len(particles), len(particles), p=weights, replace=True)
    
    # Create a new array to store resampled particles
    resampled_particles = particles[particle_indices]


    # Add noise to each resampled particle
    noise = np.random.normal(0, noise_std, resampled_particles.shape)
    resampled_particles += noise

    return resampled_particles


  ground_truth_path = []




# Utility functions 
  # Plot the path as lines
  def plot_path(path, color='r', label='path'):
    x = []
    y = []

    for i in range(len(path)):
      x.append(path[i][0])
      y.append(path[i][1])

    plt.plot(x, y, color=color,label=label)

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



  # Plotting parameters
  fig, ax = plt.subplots()  # Create a figure containing a single axes.
  plt.ion() # Turn on interactive mode



  # Main loop:
  while robot.step(timestep) != -1:

    left_motor.setVelocity(7.0)
    right_motor.setVelocity(4.5)

# Action Update
    # Iterate through all particles
    for i in range(num_particles):
      # Update every particle with the odometry
      particles[i] = update_odometry(particles[i], timestep, left_motor.getVelocity(), right_motor.getVelocity(), wheel_base, wheel_radius, motion_noise)


    # Predicted sensor data
    predicted_distances =  predicted_sensor_data(particles, obstacles)

# Measurement Update / Perception update
    # Get sensor data (distance to obstacle)
    observed_sensor_data = observation_sensor_data(obstacles, sensor_noise)

    # Compute the weights of each particle
    weights = compute_weights(observed_sensor_data, predicted_distances,  sensor_noise)

    # Resample the particles based on the weights
    particles = resample(particles, weights)

    # Compute localised robot pose by computing the mean of all the particles on all axis
    robot_pose = np.mean(particles, axis=0)

    # Actual robot position
    ground_truth_position = supervisor.getFromDef("robot").getField("translation").getSFVec3f()
    ground_truth_orientation = quat_to_eul(supervisor.getFromDef("robot").getField("rotation").getSFRotation())[2]

    # Plot the ground truth path
    ground_truth_path.append([ground_truth_position[0],ground_truth_position[1], ground_truth_orientation])
    plot_path(ground_truth_path, color='r', label='Ground truth path')


    # Plot the obstacles
    for i, obstacle in enumerate(obstacles):
      if i == 0:
        plt.plot(obstacle[0], obstacle[1], 'ro', label='Obstacle/Landmark')
      plt.plot(obstacle[0], obstacle[1], 'ro')

    # Plot the particles
    for i in range(len(particles)):
      if i == 0:
        plt.arrow(particles[i][0], particles[i][1], math.cos(particles[i][2]), math.sin(particles[i][2]), color='g', width=0.1, label="Particles")
      plt.arrow(particles[i][0], particles[i][1], math.cos(particles[i][2]), math.sin(particles[i][2]), color='g', width=0.1)

    # Plot the robot position
    plt.arrow(robot_pose[0], robot_pose[1], math.cos(robot_pose[2]), math.sin(robot_pose[2]), color='b', width=0.1, label="Robot position")

    # Set axis lengths
    plt.xlim(-6, 6)
    plt.ylim(-6, 6)

    # Set axis labels
    plt.xlabel('x')
    plt.ylabel('y')


    plt.legend()
    plt.pause(0.01) # Pause for 0.001 seconds
    plt.clf()






from math import sqrt, acos
import math
from controller import Supervisor, Motor, Compass, Robot
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from utils.plot import plot_covariance_ellipse

robot = Robot()
supervisor = Supervisor()
timestep = int(robot.getBasicTimeStep())
dt = timestep / 1000.0

# Define attempt
attempt = 2

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

# Encoders
left_encoder = robot.getDevice("wheel_left_joint_sensor")
right_encoder = robot.getDevice("wheel_right_joint_sensor")
if left_encoder is None or right_encoder is None:
    print("Could not find encoders.")
    exit()

left_encoder.enable(timestep)
right_encoder.enable(timestep)


# Robot parameters
wheel_base = 0.20225*2
wheel_radius = 0.0985

# left_motor.setVelocity(5)
# right_motor.setVelocity(10)

# Plot settings
fig, ax = plt.subplots()
plt.ion() # Interactive mode

# World parameters
landmarks = np.array([[0,-1],[2, 3],[-1, 4],[-3, 4],[3, 3],[4, -3], [-1, -4], [-5, -4], [3, -3]])

# Initial state
current_state = np.array([0, 0, 0])
previous_endcoder_values = np.zeros(2)
odometry_path = []

# Initial covariance matrix P
initial_covariance = 0.01
P = np.array([[initial_covariance, 0, 0],
              [0, initial_covariance, 0],
              [0, 0, initial_covariance]])

# Utilities
R = np.array([[0, -1], [1, 0]])  #90 deg rotation matrix


# Robot functions
def get_encoder_values():
  # Returns encoder values in radians for left and right wheels
    return np.array([left_encoder.getValue(), right_encoder.getValue()])


# Plotting functions
# def plot_covariance_ellipse(state, covariance):
#   cov_x = covariance[0,0]
#   cov_y = covariance[1,1]
#   # Remember that covariance matrix is symmetric, so cov_xy = cov_yx
#   cov_xy = covariance[0,1]

#   # Compute the eigenvalues and eigenvectors of the covariance matrix
#   center = (state[0], state[1])
#   width = 2 * np.sqrt(cov_x)
#   height = 2 * np.sqrt(cov_y)
#   angle = np.degrees(np.arctan2(cov_xy, cov_x - cov_y) / 2.0)

#   ellipse = Ellipse(xy=center, width=width, height=height, angle=angle, color='red', lw=2, alpha=0.2, label='Covariance')

#   return ellipse



# Kalman filter functions ---------------------------

def predict_state(current_state, wheel_differences, timestep_s, P=P):
  # current_state: [x, y, theta]
  # odometry: [delta_left, delta_right]
  # timestep_s: time elapsed since the last prediction
  
  # Assuming a simple kinematic model for a differential drive robot
  # Wheel_differences are the differences in the wheel angles
  delta_left, delta_right = wheel_differences

  # Wheel velocities (in rad/s)
  left_wheel_vel = delta_left / timestep_s
  right_wheel_vel = delta_right / timestep_s


  # Convert wheel angles (delta_left, delta_right) to linear and angular velocity
  v = (left_wheel_vel + right_wheel_vel) / 2.0 * wheel_radius
  w = (right_wheel_vel - left_wheel_vel) / wheel_base * wheel_radius

  # Update the state prediction using the motion model
  x_predict = current_state[0] + v * math.cos(current_state[2]) * timestep_s
  y_predict = current_state[1] + v * math.sin(current_state[2]) * timestep_s
  theta_predict = current_state[2] + w * timestep_s

  # Covariance matrix based on the motion model.
  F = np.array([[1, 0, -v * math.sin(current_state[2]) * timestep_s],
                [0, 1, v * math.cos(current_state[2]) * timestep_s],
                [0, 0, 1]])

  G = np.array([[math.cos(current_state[2]) * timestep_s, -wheel_base * (left_wheel_vel + right_wheel_vel) * math.sin(current_state[2]) * timestep_s**2],
                [math.cos(current_state[2]) * timestep_s, + wheel_base * (left_wheel_vel + right_wheel_vel) * math.sin(current_state[2]) * timestep_s**2],
                [0, timestep_s]])

  # Standard deviations of the wheel velocities
  sigma_left = 0.2
  sigma_right = 0.2
  Q = np.array([[sigma_left**2, 0],
                [0, sigma_right**2]])

  # Update the covariance matrix
  P = F @ P @ F.T + G @ Q @ G.T


  return np.array([x_predict, y_predict, theta_predict]), P

# Observe the environment based on the actual location of the robot. 
def observe(landmarks, noise=0.0):
  position = supervisor.getFromDef("robot").getField("translation").getSFVec3f()

  differences = get_measurement(landmarks, position)

  # Add noise
  differences += np.random.normal(0, noise, differences.shape)

  return differences, position

def predict_observation(predicted_state, landmarks):
  # Compute the vectors from the predicted robot state to the landmarks
  landmark_predictions = get_measurement(landmarks, predicted_state)
  
  # Retuen the predicted observations
  return landmark_predictions

def get_measurement(landmarks, state):
  measurements = np.zeros((len(landmarks),3))
  for j, landmark in enumerate(landmarks):
    measurements[j][:2] = landmark - state[:2]
    # Compute the angle between the robots heading to the landmark
    measurements[j][2] = np.arctan2(landmark[1] - state[1], landmark[0] - state[0]) - state[2]
  return measurements



def landmark_matching(landmarks, predicted_observation, threshold=0.1):
  # Landmark matching based on euclidean distance between the predicted and actual observations

  # List to store the landmark matches
  landmark_matches = []

  for landmark in landmarks:
    min_distance = float('inf')
    for pred_obs in predicted_observation:
      # Compute the euclidean distance between the predicted and actual observations
      euclidean_distance = np.sqrt((obs[0] - pred_obs[0])**2 + (obs[1] - pred_obs[1])**2)

      if euclidean_distance < min_distance:
        min_distance = euclidean_distance
        closest_landmark = landmark

      # If the distance is small enough, we can assume that the predicted and actual observations are the same
      if euclidean_distance < threshold:
        landmark_matches.append([landmark, pred_obs])
  print(f"landmark_matches: {landmark_matches}")
        
  return landmark_matches

def update_state(current_state, predicted_state, landmark_matches):
  # Update using Kalman Gain

  # Compute the Kalman Gain
  K = calculate_kalman_gain(current_state, landmark_matches)

  # Innovation
  innovation = predicted_state - predict_observation(current_state, landmarks)

  # Update the state
  state_updated = current_state + K @ innovation

  return state_updated

def calculate_kalman_gain(current_state, landmark_matches):
  # Compute the measurement Jacobian
  H = calculate_measurement_jacobian(current_state, landmark_matches)

  print(f"H: {H}")
  print(f"shape H: {H.shape}")

  print(f"P: {P}")
  print(f"shape P: {P.shape}")

  print(f"R: {R}")
  print(f"shape R: {R.shape}")

  print(f"H @ P @ H.T {H @ P @ H.T}")
  print(f"np.linalg.inv(H @ P @ H.T + R): {np.linalg.inv(H @ P @ H.T)}")

  # Compute the Kalman Gain
  K = P @ H.T @ np.linalg.inv(H @ P @ H.T)

  return K

def calculate_measurement_jacobian(current_state, landmark_matches):
  # Compute the measurement Jacobian
  H = np.zeros((len(landmark_matches), 3))
  for i, landmark_match in enumerate(landmark_matches):
    # landmark = landmark_match[0]
    # H[i] = np.array([-(landmark[0] - current_state[0]) / np.sqrt((landmark[0] - current_state[0])**2 + (landmark[1] - current_state[1])**2), -(landmark[1] - current_state[1]) / np.sqrt((landmark[0] - current_state[0])**2 + (landmark[1] - current_state[1])**2)])
    H[i] = -1
  return H

while robot.step(timestep) != -1 and attempt == 1:
  # Read the sensors:
  encoder_values = get_encoder_values()  
  # Compute the wheel differences
  wheel_differences = encoder_values - previous_endcoder_values
  # Update the previous wheel differences
  previous_endcoder_values = encoder_values
  

  # Predict the state
  predicted_state, P = predict_state(current_state, wheel_differences, dt, P=P)
  # Plot the covariance matrix
  ellipse = plot_covariance_ellipse(predicted_state, P)
  plt.gca().add_patch(ellipse)

  # Plot the state
  # Append the state to the path
  odometry_path.append(current_state)
  x = [odometry_path[i][0] for i in range(len(odometry_path))]
  y = [odometry_path[i][1] for i in range(len(odometry_path))]
  plt.plot(x, y, 'r')


  # Observe the environment
    # The observation is in the sensor frame.
  observation, actual_position = observe(landmarks, noise=0.01)
  # Plot the observation
  for obs in observation:
    plt.plot([obs[0] + actual_position[0], actual_position[0]], [obs[1] + actual_position[1], actual_position[1]], 'g')


  # Predict the observation
  predicted_observation = predict_observation(predicted_state, landmarks)
  # Plot the predicted measurements in global frame
  for predicted_obs in predicted_observation:
    plt.plot([predicted_obs[0] + predicted_state[0], predicted_state[0]], [predicted_obs[1] + predicted_state[1], predicted_state[1]], 'black')

  print(f"predicted_observation: {predicted_observation}")
  print(f"predicted_observation.shape: {predicted_observation.shape}")


  # Landmark matching
  matches = landmark_matching(landmarks, predicted_observation, threshold=0.1)

  best_state_estimate = update_state(current_state, predicted_state, matches)
  

  # Update the state
  current_state = best_state_estimate

  # current_state = predicted_state


  # Plotting ---------------------------
  # Plot the landmarks
  for landmark in landmarks:
    plt.plot(landmark[0], landmark[1], 'bo')

  # Set axis lengths
  plt.xlim(-6, 6)
  plt.ylim(-6, 6)

  # Set axis labels
  plt.xlabel('x')
  plt.ylabel('y')
  plt.pause(0.001)
  plt.clf()

  pass




# 2nd attempt --------------------------------------------------------------
# First define the states:
# x: x-position
# y: y-position
# theta: heading
# v: linear velocity (include to square the jacobians)

# Motion model covariance Q
Q = np.diag([ 0.1,               # x
              0.1,               # y
              np.deg2rad(1.0),   # theta
              1.0]) **2          # v

# Predict state covariance R
R = np.diag([1.0, 1.0]) **2 # Observation x,y covariance

# Input noise
INPUT_NOISE = np.diag([0.7, np.deg2rad(10.0)]) **2
GPS_NOISE = np.diag([0.5, 0.5]) ** 2

DT = timestep / 1000.0 # Time step s


# Compute Input
def calc_input(previous_endcoder_values):
  """Compute the control input value u based on encoder values

  Args:
      previous_endcoder_values (np.array(2)): Array containing the previous encoder values

  Returns:
      np.array(2): liear and angular velocity
  """

  left_encoder_measurement = left_encoder.getValue()
  right_encoder_measurement = right_encoder.getValue()

  # Compute the wheel differences
  left_diff = left_encoder_measurement - previous_endcoder_values[0]
  right_diff = right_encoder_measurement - previous_endcoder_values[1]

  # Incorporate the timedifference
  left_wheel_ang_vel = left_diff / DT
  right_wheel_ang_vel = right_diff / DT

  
  # Linear velocity is the average of the left and right wheel velocities
  v = (left_wheel_ang_vel + right_wheel_ang_vel) / 2.0 * wheel_radius # m/s
  omega = (right_wheel_ang_vel - left_wheel_ang_vel) / wheel_base * wheel_radius # rad/s

  # v = 1.0 # m/s
  # omega = 0.1 # rad/s
  u = np.array([[v], [omega]])


  return u, np.array([left_encoder_measurement, right_encoder_measurement])

def get_observation(true_state, predicted_state, u):
  # Get the true state of the robot
  true_state = motion_model(true_state, u)

  # z = h(x) + v
  observation = observation_model(true_state) + GPS_NOISE @ np.random.randn(2,1) 

  # Add noise to input
  ud = u + INPUT_NOISE @ np.random.randn(2,1)

  # Predict the state with noise added
  predicted_state = motion_model(predicted_state, ud)

  return true_state, observation, predicted_state, ud



def motion_model(x, u):
  # We only want to extract the first 3 states from the state vector
  F = np.array([[1.0, 0, 0, 0],
                [0, 1.0, 0, 0],
                [0, 0, 1.0, 0],
                [0, 0, 0, 0]])
  
  # Control input matrix
  B = np.array([[DT * math.cos(x[2, 0]), 0],
                [DT * math.sin(x[2, 0]), 0],
                [0.0, DT],
                [1.0, 0.0]])
  
  # Predict the state
  x = F @ x + B @ u

  return x

def observation_model(x):
  H = np.array([[1, 0, 0, 0],
                [0, 1, 0, 0]])

  # observation, z = h(x). We only observe the position
  z = H @ x


  return z


def jacob_f(x, u):
  # Jacobian of the motion model

  # motion model
  # x_{t+1} = x_t+v*dt*cos(yaw)
  # y_{t+1} = y_t+v*dt*sin(yaw)
  # yaw_{t+1} = yaw_t+omega*dt
  # v_{t+1} = v{t}

  # Partial derivatives
  # dx/dyaw = -v*dt*sin(yaw)
  # dx/dv = dt*cos(yaw)
  # dy/dyaw = v*dt*cos(yaw)
  # dy/dv = dt*sin(yaw)

  yaw = x[2, 0]
  v = u[0, 0]

  jF = np.array([[1.0, 0.0, -DT * v * math.sin(yaw), DT * math.cos(yaw)],
                 [0.0, 1.0, DT * v * math.cos(yaw), DT * math.sin(yaw)],
                 [0.0, 0.0, 1.0, 0.0],
                 [0.0, 0.0, 0.0, 1.0]])

  return jF


def jacob_h():
  # Jacobian of the observation model
  jH = np.array([[1, 0, 0, 0],
                 [0, 1, 0, 0]])

  return jH

def ekf_estimation(state_estimate, estimation_covariance, z, u):
# Predict
  state_prediction = motion_model(state_estimate, u)
  # Motion model Jacobian
  jF = jacob_f(state_estimate, u) 
  # Covariance prediction using propagation of uncertainty of the motion model
  prediction_P = jF @ estimation_covariance @ jF.T + Q

# Update 
  observation_jacobian = jacob_h()
  observation_prediction = observation_model(state_prediction)
  # innovation 
  y = z - observation_prediction
  # Kalman gain
  K = prediction_P @ observation_jacobian.T @ np.linalg.inv(observation_jacobian @ prediction_P @ observation_jacobian.T + R)

  # Update the state estimate using the kalman gain to reduce position error 
  state_estimate = state_prediction + K @ y
  # Update covariance
  estimation_covariance = (np.eye(len(state_estimate)) - K @ observation_jacobian) @ prediction_P

  return state_estimate, estimation_covariance


# Initial state
state_estimate = np.zeros((4,1))
true_state = np.zeros((4,1))
covariance_estimate = np.eye(4)

# odometry / dead reckoning
state_dead_reckoning = np.zeros((4,1))

# Previous values
prev_state_estimate = state_estimate
prev_true_state = true_state
prev_state_dead_reckoning = true_state 
prev_observation = np.zeros((2,1))

prev_encoder_values = np.zeros(2)

# Set wheel velocities
left_motor.setVelocity(1.5)
right_motor.setVelocity(3.0)



def done():
  print("Done")
  supervisor.simulationSetMode(supervisor.SIMULATION_MODE_PAUSE)
  exit(0)

while robot.step(timestep) != -1:
  # Compute the control input value u based on proprioceptive encoder values
  u, prev_encoder_values = calc_input(prev_encoder_values)

  true_state, observation, state_dead_reckoning, ud = get_observation(true_state, state_dead_reckoning, u)

  state_estimate, covariance_estimate = ekf_estimation(state_estimate, covariance_estimate, observation, ud)

  # Update previous values to keep track of the path
  prev_state_estimate = np.hstack((prev_state_estimate, state_estimate))
  prev_true_state = np.hstack((prev_true_state, true_state))
  prev_state_dead_reckoning =  np.hstack((prev_state_dead_reckoning, state_dead_reckoning))
  prev_observation = np.hstack((prev_observation, observation))

  plt.cla()
  # Stop the simulation with the escape key
  plt.gcf().canvas.mpl_connect('key_release_event', lambda event: [done() if event.key == 'escape' else None])

  plt.plot(prev_observation[0, :], prev_observation[1, :], '.g', label='Observation')
  plt.plot(prev_true_state[0, :].flatten(),prev_true_state[1, :].flatten(), "-b", label='True state')
  plt.plot(prev_state_dead_reckoning[0, :].flatten(),prev_state_dead_reckoning[1, :].flatten(), "-k", label='Dead reckoning')
  plt.plot(prev_state_estimate[0, :].flatten(),prev_state_estimate[1, :].flatten(), "-r", label='State estimate')

  plot_covariance_ellipse(state_estimate[0,0], state_estimate[1,0], covariance_estimate, chi2=3.0)

  plt.axis("equal")
  plt.xlim(-6, 6)
  plt.ylim(-6, 6)
  plt.legend()
  plt.grid(True)
  plt.pause(0.001)




"""bug1 controller."""

from math import sqrt, acos
from controller import Supervisor, Lidar, Motor, Node, Field
import matplotlib.pyplot as plt
import numpy as np
import math

GOAL_POINT = [4.0, 4.0, 0.0]

WHEEL_BASE_RADIUS = 0.2  # taken from Webots PROTO
WHEEL_RADIUS = 0.0985  # taken from Webots PROTO
TARGET_FORWARD_VELOCITY = 0.1  # m/s, tweak this to your liking.
MAX_WHEEL_VELOCITY = 6  # TIGAo in webots is set to 10.15
LIDAR_FOV = 6.28  # radians
OBJECT_HIT_DIST = 0.8  # when do we consider a hit-point? in m.
OBJECT_FOLLOW_DIST = 0.8  # How closely do we follow the obstacle? in m.

robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

# LIDAR
top_lidar = Lidar("lidar")
# The user guide recommends to use robot.getDevice("top_lidar"), but pylint has
# a hard time finding the type of the return value. This also style works fine
# for me.
if top_lidar is None:
    print("Could not find a lidar.")
    exit()
# enable takes one argument, namely the sampling period in ms
top_lidar.enable(100)

# MOTORS
# Find motors and set them up to velocity control
left_motor = Motor("wheel_left_joint")
# Same as with the lidar above: robot.getDevice("wheel_left_joint")
right_motor = Motor("wheel_right_joint")

if left_motor is None or right_motor is None:
    print("Could not find motors.")
    exit()
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
# left_motor.setAcceleration(-1)
# right_motor.setAcceleration(-1)
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)


def set_velocities(linear_vel, angular_vel):
    """Set linear and angular velocities of the robot.

    Arguments:
    linear_velocity  -- Forward velocity in m/s.
    angular_velocity -- Rotational velocity rad/s. Positive direction is
                        counter-clockwise.
    """
    diff_vel = angular_vel * WHEEL_BASE_RADIUS / WHEEL_RADIUS
    right_vel = (linear_vel + diff_vel) / WHEEL_RADIUS
    left_vel = (linear_vel - diff_vel) / WHEEL_RADIUS
    fastest_wheel = abs(max(right_vel, left_vel))
    if fastest_wheel > MAX_WHEEL_VELOCITY:
        left_vel = left_vel / fastest_wheel * MAX_WHEEL_VELOCITY
        right_vel = right_vel / fastest_wheel * MAX_WHEEL_VELOCITY
    left_motor.setVelocity(left_vel)
    right_motor.setVelocity(right_vel)


def pure_pursuit(x_track_error, angle_error):
    """Follow a line.

    Arguments:
    x_track_error -- Cross-track error. The distance error perpendicular to the
                     reference line. If the robot is located to the left of the
                     line,it gives a positive error; negative to the right.
    angle_error   -- Angle error is the difference between the angle of the line
                     and the heading of the robot. If the reference line points
                     towards North and the robot to East, the error is positive;
                     negative to West.
    """
    ang_vel = - 0.05 * x_track_error + 0.1 * angle_error
    set_velocities(TARGET_FORWARD_VELOCITY, ang_vel)


def get_my_location():
    """Gets the robots translation in the world."""
    return robot.getSelf().getPosition()


def get_my_orientation():
    """Gets the robots orientation in the worldd"""
    return robot.getSelf().getOrientation()


def angle_to_object(ranges):
    """Find the angle that points to the closest lidar point.

    We will assume that the lidar is mounted symmetrically, so that the center
    lidar point is at the front of the robot. We will return this as 0 rads.
    """
    index_min = min(range(len(ranges)), key=ranges.__getitem__)
    angle = LIDAR_FOV*0.5 - LIDAR_FOV*float(index_min) / float(len(ranges) - 1)
    distance = ranges[index_min]
    return angle, distance


def heading_difference(start_point, end_point):
    """Get the angle difference between the robot heading and a line

    The line is defined by a start and an end point. The angle between the
    heading and the line is given by the dot product. To get orientation
    we need to look at the direction of the cross product along the z-axis.
    """
    rot_robot = np.array(robot.getSelf().getOrientation()).reshape(3, 3)
    robot_heading = np.dot(rot_robot, np.array([1, 0, 0]))
    line = (np.array(end_point) - np.array(start_point))
    angle = acos(np.dot(robot_heading, line)
                 / np.linalg.norm(line)
                 / np.linalg.norm(robot_heading))
    cross = np.cross(line, robot_heading)
    if cross[2] > 0.0:
        angle = -angle

    return angle


def distance_to(goal_location):
    """Get the current distance to a goal"""
    my_location = get_my_location()
    dist = np.linalg.norm(np.array(goal_location) - np.array(my_location))
    return dist


def distance_to_line(start_point, end_point):
    """Compute robot's perpendicular distance from the robot to a line.

    The line is defined by a start- and an end-point.

    The robot is assumed to move only in the x/y plane. So a normal vector (n)
    is computed between the line (B-A) and the z-unit vector. The projection of
    the current location (P) onto the normal vector gives the distance.
    """
    A = np.array(start_point)
    B = np.array(end_point)
    P = np.array(get_my_location())
    n = np.cross([0, 0, 1], (B-A))
    distance = np.dot((P-A), n)/np.linalg.norm(n)
    return distance


def place_marker(robot_translation):
    """Place a marker at the robot's location."""
    root = robot.getRoot()
    world_children = root.getField("children")
    world_children.importMFNodeFromString(
        -1,
        """
    Transform {{
        translation {} {} {}
        children [
            Shape {{
            appearance PBRAppearance {{
                baseColor 0.8 0 0
            }}
            geometry Sphere {{
                radius 0.1
            }}
            }}
        ]
    }}
    """.format(
            robot_translation[0], robot_translation[1], robot_translation[2]
        ),
    )


def attractiveGradient(zeta, q, q_goal, threshold):
    """Attractive Gradient with magnitude proportional to the distance from the goal.
    Parameters:

    Returns:
        U_Attrative: Magnitude proportional to the distance from the goal.
    """
    # Compute the relative position from the robot configuration q to the goal q_goal
    relativePosition = [(q_goal[i] - q[i]) for i in range(3)]
    # Determine if conic or quadratic potential should be used.
    if (distance_to(q_goal) <= threshold):
        return [zeta*relativePosition[i] for i in range(3)]
    else:
        return [threshold*zeta*relativePosition[i]/distance_to(q_goal) for i in range(3)]


def repulsiveGradient(eta, Q, q,  ranges):
    """Compute repulsive gradient force to the closest obstacle.
    Parameters:
      eta: Magnitude/gain of the repulsive force.
      Q: Distance threshold to ignore obstacles sufficiently far away.
      q: Robot configuration.
      ranges: Lidar measurements.

    Returns:
        List[float64]: 3D vector of the repulsive force.
    """

    # Get angle and distance to closest object
    angle, dist = angle_to_object(ranges)
    print(f"angle: {angle}")
    # compute the distance vector from the robot to the object
    d_qc = [0 for i in range(3)]
    d_qc[0] = math.cos(angle)*dist + math.pi /2
    d_qc[1] = math.sin(angle)*dist 
    # Compute the repulsive force. 
    return [eta*(1/Q - 1/dist)*1/pow(dist, 2)*d_qc[i] for i in range(3)]


def example_main():

    # Wait a moment to get the first lidar scan
    robot.step(500)

    # initialize leave-point to initial location
    initial_location = get_my_location()

    while True:
        ranges = top_lidar.getRangeImage()
        # While the robot is not at the goal and not close to an object
        while (robot.step(timestep) != -1 and distance_to(GOAL_POINT) > OBJECT_HIT_DIST and not any(r < OBJECT_HIT_DIST for r in ranges)): 
            ranges = top_lidar.getRangeImage()
            # Get the distance to the 
            x_track_error = distance_to_line(leave_point, GOAL_POINT)
            heading_error = heading_difference(leave_point, GOAL_POINT)
            print([x_track_error, heading_error])
            pure_pursuit(x_track_error, heading_error)
        if distance_to(GOAL_POINT) < OBJECT_HIT_DIST:
            exit()

        current_location = get_my_location()
        place_marker(current_location)
        hit_location = current_location
        returning_to_hit = False
        hit_location_reencountered = False
        closest_goal_distance = float('inf')

        while (robot.step(timestep) != -1 and
                distance_to(GOAL_POINT) > OBJECT_HIT_DIST and
                not hit_location_reencountered):
            ranges = top_lidar.getRangeImage()
            angle = angle_to_object(ranges)
            dist = min(ranges)

            # print(current_distance_to_m)
            # we will try and keep the set distance
            # turning to right, so 90 degrees is added to the reference.
            pure_pursuit(OBJECT_FOLLOW_DIST - dist, angle - 1.578)
            # Track next leave point
            current_goal_distance = distance_to(GOAL_POINT)
            if closest_goal_distance > current_goal_distance:
                closest_goal_distance = current_goal_distance
                leave_point = get_my_location()
            # Keep the robot from instantly thinking that it returned to hit
            if not returning_to_hit and distance_to(hit_location) > OBJECT_HIT_DIST:
                returning_to_hit = True
            if returning_to_hit and distance_to(hit_location) < OBJECT_HIT_DIST:
                hit_location_reencountered = True
                place_marker(leave_point)

        while (robot.step(timestep) != -1 and
                distance_to(leave_point) > OBJECT_HIT_DIST):
            ranges = top_lidar.getRangeImage()
            angle = angle_to_object(ranges)
            dist = min(ranges)
            # we will try and keep the set distance
            # turning to right, so 90 degrees is added to the reference.
            pure_pursuit(OBJECT_FOLLOW_DIST - dist, angle - 1.578)


def complete_bug2():
    # Wait a moment to get the first lidar scan
    robot.step(500)

    # initialize leave-point to initial location
    initial_location = get_my_location()
    leave_point = initial_location

    while True:
        ranges = top_lidar.getRangeImage()
        while (robot.step(timestep) != -1 and
                distance_to(GOAL_POINT) > OBJECT_HIT_DIST and
                not any(r < OBJECT_HIT_DIST for r in ranges)):
            ranges = top_lidar.getRangeImage()
            x_track_error = distance_to_line(leave_point, GOAL_POINT)
            heading_error = heading_difference(leave_point, GOAL_POINT)
            # print([x_track_error, heading_error])
            pure_pursuit(x_track_error, heading_error)
        if distance_to(GOAL_POINT) < OBJECT_HIT_DIST:
            exit()
        print("test")

        current_location = get_my_location()
        place_marker(current_location)
        hit_location = current_location
        returning_to_hit = False
        hit_location_reencountered = False
        has_moved_away_from_m = False
        m_reencountered = False
        closest_goal_distance = float('inf')

        current_distance_to_m = distance_to_line(initial_location, GOAL_POINT)

        while (robot.step(timestep) != -1 and
                distance_to(GOAL_POINT) > OBJECT_HIT_DIST and
                not m_reencountered):
            ranges = top_lidar.getRangeImage()
            angle = angle_to_object(ranges)
            dist = min(ranges)

            current_distance_to_m = abs(
                distance_to_line(initial_location, GOAL_POINT))
            print(current_distance_to_m)
            if current_distance_to_m > OBJECT_HIT_DIST and not has_moved_away_from_m:
                has_moved_away_from_m = True

            # we will try and keep the set distance
            # turning to right, so 90 degrees is added to the reference.
            pure_pursuit(OBJECT_FOLLOW_DIST - dist, angle - 1.578)
            # Track next leave point
            # current_goal_distance = distance_to(GOAL_POINT)
            # if closest_goal_distance > current_goal_distance:
            # closest_goal_distance = current_goal_distance
            # leave_point = get_my_location()

            # # Keep the robot from instantly thinking that it returned to hit
            if has_moved_away_from_m and current_distance_to_m < OBJECT_HIT_DIST:
                m_reencountered = True
                leavepoint = get_my_location()
                has_moved_away_from_m = False
                place_marker(leavepoint)

            if (not hit_location_reencountered and distance_to(hit_location) < OBJECT_HIT_DIST and has_moved_away_from_m):
                hit_location_reencountered = True
                print("Goal is unreachable")
                exit()

        # while (robot.step(timestep) != -1 and
                # distance_to(leave_point) > OBJECT_HIT_DIST):
            # ranges = top_lidar.getRangeImage()
            # angle = angle_to_object(ranges)
            # dist = min(ranges)
            # we will try and keep the set distance
            # turning to right, so 90 degrees is added to the reference.
            # pure_pursuit(OBJECT_FOLLOW_DIST - dist, angle - 1.578)
    set_velocities(0.0, 0)


vertecies = [(-10, 10), (-10, -10), (-3*math.sqrt(2), 0), (0, 3*math.sqrt(2)),
             (0, -3*math.sqrt(2)), (3*math.sqrt(2), 0), (10, 10), (10, -10)]


def connectTwoVertecies(p1, p2, color):
    x1, x2 = p1[0], p2[0]
    y1, y2 = p1[1], p2[1]
    plt.plot([x1, x2], [y1, y2], color)


def plotVertecies(vertecies):
    vertex_x = [i for i, j in vertecies]
    vertex_y = [j for i, j in vertecies]
    plt.plot(vertex_x, vertex_y, 'ro')

    # Boundary
    connectTwoVertecies(vertecies[0], vertecies[1], 'k-')
    connectTwoVertecies(vertecies[0], vertecies[6], 'k-')
    connectTwoVertecies(vertecies[1], vertecies[7], 'k-')
    connectTwoVertecies(vertecies[6], vertecies[7], 'k-')

    # Obstacle
    connectTwoVertecies(vertecies[2], vertecies[3], 'k-')
    connectTwoVertecies(vertecies[3], vertecies[5], 'k-')
    connectTwoVertecies(vertecies[5], vertecies[4], 'k-')
    connectTwoVertecies(vertecies[2], vertecies[4], 'k-')

    # Decomposition
    connectTwoVertecies(vertecies[0], vertecies[2], 'red')
    connectTwoVertecies(vertecies[0], vertecies[3], 'red')

    connectTwoVertecies(vertecies[3], vertecies[6], 'red')
    connectTwoVertecies(vertecies[5], vertecies[6], 'red')

    connectTwoVertecies(vertecies[5], vertecies[7], 'red')
    connectTwoVertecies(vertecies[4], vertecies[7], 'red')

    connectTwoVertecies(vertecies[1], vertecies[2], 'red')
    connectTwoVertecies(vertecies[1], vertecies[4], 'red')

    plt.axis('equal')
    plt.show()


def trapezoidalDecomposition():
    plotVertecies(vertecies)


def potentialField():
    # Wait a moment to get the first lidar scan
    robot.step(500)

    counter = 0
    # initialize leave-point to initial location
    while robot.step(timestep) != -1:
        ranges = top_lidar.getRangeImage()
        currentLocation = get_my_location()
        # Compute the acctractive and repulsive gradients. The attractive is stronger than the repulsive
        att = attractiveGradient(25, currentLocation, GOAL_POINT, 2)
        rep = repulsiveGradient(20, 20*WHEEL_BASE_RADIUS, currentLocation, ranges)

        sum = [att[i] + rep[i] for i in range(3)]
        print(f"Sum: {sum}")
        if (counter == 100):
            pose = [currentLocation[0],
                    currentLocation[1], distance_to(att)/10]
            place_marker(pose)
            counter = 0
        counter += 1

        print(f"Force: {distance_to(sum)}")
        print(f"Goal: {distance_to(GOAL_POINT)}")


        if distance_to(GOAL_POINT) <= 0.5:
            print(f"goal_reached")
            set_velocities(0, 0)
            break

        pure_pursuit(distance_to_line(currentLocation, sum),
                     heading_difference(currentLocation, sum))


def main():
    """Main function, runs when the program starts."""
    while robot.step(timestep) != -1:

        robot.step(500)

        initial_position = get_my_location()
        print(initial_position)
        set_velocities(0.5, 0)
        ranges = top_lidar.getRangeImage()


if __name__ == "__main__":
    # main()
    # complete_bug2()
    potentialField()
    # trapezoidalDecomposition()
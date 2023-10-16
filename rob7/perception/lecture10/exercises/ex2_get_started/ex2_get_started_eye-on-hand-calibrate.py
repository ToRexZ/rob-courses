import numpy as np
import cv2
import matplotlib.pyplot as plt
import glob


# Load the transformation from the saved kinematics
# as a nested set of dicts.
# The transformation information can be accessed as:
# R = kinematics['image42.png']['R']
def load_kinematics(path):
    kinematics = {}

    firstLine = True
    with open(path, "r") as f:
        for line in f:
            # Skip first line / the header
            if firstLine:
                firstLine = False
                continue

            # Split into values based on comma-separator
            values = line.split(",")

            image_name = str(values[0])
            curr_transform = {}
            curr_transform["t"] = np.array(values[1:4], np.float32)

            if len(values) == 7:  # must be using Rodrigues format
                curr_transform["R"], _ = cv2.Rodrigues(np.array(values[4:], np.float32))
            elif len(values) == 13:  # must be a rotation matrix
                curr_transform["R"] = np.array(values[4:], np.float32).reshape(3, 3)
            else:  # neither - something is wrong!
                print("Error! Badly formatted input file!")
            kinematics[image_name] = curr_transform
    return kinematics


# Load camera calibration from earlier
# along with extrinsics for each checkerboard
# i.e. rotation and translation
with np.load("ur-cam-cal.npz") as npz:
    print(list(npz.keys()))
    mtx = npz["projection_mat"]
    dists = npz["distortion"]
    rvecs = npz["rotations"]
    tvecs = npz["translations"]
    image_names = list(npz["image_names"])

print(image_names)

kinematics_gripper2base = load_kinematics(
    "./data/UR-calibration/kinematics-gripper2base.txt"
)


# Extract the rotation matrics and translation vectors
# from the file containing the kinematic information
R_gripper2base = []
t_gripper2base = []

# Only load the kinematic information for the image
# where we succeeded in detecting the checkerboard
# i.e. the image names contained in 'image_names'
for img_path in image_names:
    img_name = img_path.split("/")[-1]
    R_gripper2base.append(kinematics_gripper2base[img_name]["R"])
    t_gripper2base.append(kinematics_gripper2base[img_name]["t"])

# Luckily the gripper2base transform is just
# what we need for doing a eye-in-hand calibration - how convenient!
R_cam2gripper, t_cam2gripper = cv2.calibrateHandEye(
    R_gripper2base, t_gripper2base, rvecs, tvecs, method=cv2.CALIB_HAND_EYE_TSAI
)

print(R_cam2gripper)
print(t_cam2gripper)

# As the translation is given as approximately (0, -52, 98) this makes sense relative to the setup. The rotation is very small relative to the gripper head, so it has great alignment.

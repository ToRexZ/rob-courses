import numpy as np
import cv2
import glob

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

# Find the index corresponding to image 'image16.png'
img_idx = image_names.index("./data/UR-calibration/images/image16.png")

# Load that image
img = cv2.imread(image_names[img_idx])

# And the corresponding extrinsinc params
rotation = rvecs[img_idx]
translation = tvecs[img_idx]

# Prepare the list of 3D points
pts_world = np.float32([[0.0, 0.0, 0.0], [50.0, 50.0, 0.0]])

# Project the 3D points to image coords
pts_img, _ = cv2.projectPoints(pts_world, rotation, translation, mtx, dists)

# Draw the points
for p in pts_img:
    img = cv2.circle(img, (int(p[0][0]), int(p[0][1])), 12, (255, 0, 0), 6)

cv2.imwrite("projected_points.jpeg", img)

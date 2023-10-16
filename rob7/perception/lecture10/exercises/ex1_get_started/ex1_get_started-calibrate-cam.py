import numpy as np
import cv2
import glob
import matplotlib.pyplot as plt

# Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,9,0)
board_size = (8, 6)
pts_obj = np.zeros((board_size[0] * board_size[1], 3), np.float32)
pts_obj[:, :2] = np.mgrid[0 : board_size[0], 0 : board_size[1]].T.reshape(-1, 2)

# Scale the object points to correspond with the actual size of the squares
square_size = 12.5  # i.e. 20 mm
pts_obj *= square_size

# Arrays to store object points and image points from all the images.
all_pts_obj = []  # 3d point in real world space
all_pts_img = []  # 2d points in image plane.
image_names = []  # names of processed images
images = glob.glob("./data/UR-calibration/images/*.png")


# Loop through all the images
for fname in images:
    print(fname)
    # Loop image and convert to grayscale
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, board_size, None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        # Refine detected image points
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners2 = cv2.cornerSubPix(gray, corners, (3, 3), (-1, -1), criteria)

        # Store object points and image points for calibration later
        all_pts_obj.append(pts_obj)
        all_pts_img.append(corners2)

        # Store name of the image file
        image_names.append(fname)

        # Draw and display the corners
        cv2.drawChessboardCorners(img, board_size, corners2, ret)

        # Uncomment to display detected points
        # plt.figure("Detected points")
        # plt.imshow(img)
        # plt.show()

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    all_pts_obj, all_pts_img, gray.shape[::-1], None, None
)

print("Projection matrix: ", mtx)
print("Lens distortion: ", dist)
print("Rotations: ", rvecs)
print("Translations: ", tvecs)

# Save the results to a npz file
np.savez(
    "ur-cam-cal.npz",
    projection_mat=mtx,
    distortion=dist,
    rotations=rvecs,
    translations=tvecs,
    image_names=image_names,
)

import numpy as np
import cv2
from matplotlib import pyplot as plt
import os

# Get the path to the folder tsukuba
folder = os.path.join(os.getcwd(), "tsukuba")


# folder = os.path.join(os.getcwd(), "exec1-get-started", "tsukuba")

file1 = os.path.join(folder, "scene1.row3.col1.ppm")
file2 = os.path.join(folder, "scene1.row3.col3.ppm")


# import files from the tsukuba folder using cv2.imread
def import_files(folder):
    files = []
    for file in os.listdir(folder):
        if file.endswith(".ppm"):
            files.append(os.path.join(folder, file))
    return files


# Read the files returned by import_files as grayscale images
def read_files(files):
    images = []
    for file in files:
        images.append(cv2.imread(file, cv2.IMREAD_GRAYSCALE))
    return images


print(read_files(import_files(folder)))

print(folder)

# Read the read and left stereo image pair
imgR = cv2.imread(
    file1,
    cv2.IMREAD_GRAYSCALE,
)
imgL = cv2.imread(
    file2,
    cv2.IMREAD_GRAYSCALE,
)

# Calculate disparity map
stereo = cv2.StereoBM.create(numDisparities=16, blockSize=15)

disparity = stereo.compute(imgL, imgR)
plt.title("disparity map")
plt.imshow(disparity, "gray")
plt.show()

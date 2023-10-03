import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt


filename1 = "./sprites/aau-city-1.jpg"
filename2 = "./sprites/aau-city-2.jpg"
img1 = cv.imread(filename1)
img1_gray = cv.imread(filename1, cv.IMREAD_GRAYSCALE)
img2 = cv.imread(filename2)
img2_gray = cv.imread(filename2, cv.IMREAD_GRAYSCALE)
assert img1 is not None, "File could not be read, check with os.path.exists()"
assert img2 is not None, "File could not be read, check with os.path.exists()"

plt.subplot(231), plt.imshow(img1, cmap="gray")
plt.title("Original image"), plt.xticks([]), plt.yticks([])

# Convert to grayscale
img_gray = cv.cvtColor(img1, cv.COLOR_RGB2GRAY)

# Blur the image for better edge detection
img_blur = cv.GaussianBlur(img_gray, (3, 3), 0)


# Sobel Kernels
sobelx = cv.Sobel(src=img_blur, ddepth=cv.CV_64F, dx=1, dy=0, ksize=5)
sobelx = cv.Sobel(src=img_blur, ddepth=cv.CV_64F, dx=0, dy=1, ksize=5)
sobelxy = cv.Sobel(src=img_blur, ddepth=cv.CV_64F, dx=1, dy=1, ksize=5)


# Lecture2: Exercise 1: Scale Invarient Feature Transform


sift = cv.SIFT_create()

# Find keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

# BFMatcher with default parameters
bf = cv.BFMatcher()
matches = bf.knnMatch(des1, des2, k=2)

# Apply ratio test:
good = []
goodknn = []
for m, n in matches:
    if m.distance < 0.15 * n.distance:
        goodknn.append([m])
        good.append(m)

# cv.drawMatchesKNN expects list of lists as matches
img3 = cv.drawMatchesKnn(
    img1,
    kp1,
    img2,
    kp2,
    goodknn,
    None,
    flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS,
)

keypointImg = cv.drawKeypoints(img1, kp1, img1)


# Exercise 2: Use A Homography which includes RANSAC to calculate the transformation between the two images (look at findHomography() and warpPerspective())

src_pts1 = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
dst_pts1 = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

M, mask = cv.findHomography(src_pts1, dst_pts1, cv.RANSAC, 5.0)

matchesMask = mask.ravel().tolist()

h, w = img1_gray.shape
pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
dst = cv.perspectiveTransform(pts, M)
img2_gray = cv.polylines(img2_gray, [np.int32(dst)], True, 255, 3, cv.LINE_AA)

print(dst)

draw_params = dict(
    matchColor=(0, 255, 0),  # draw matches in green color
    singlePointColor=None,
    matchesMask=matchesMask,  # Only draw inliners
    flags=2,
)

# We draw the lines with the inliers.
img4 = cv.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)


# Draw a warped perspective image, which takes the input image and outputs a transformed image based on the transformation matrix M.
img5 = cv.warpPerspective(img1_gray, M, (w, h), flags=cv.INTER_LINEAR)


plt.subplot(232), plt.imshow(sobelxy, cmap="gray")
plt.title("Edge Image"), plt.xticks([]), plt.yticks([])
# (num_rows, num_cols, index counting left to right, then top to bottom.)
plt.subplot(233), plt.imshow(keypointImg, cmap="gray")
plt.title("SIFT"), plt.xticks([]), plt.yticks([])
plt.subplot(234), plt.imshow(img3, cmap="gray")
plt.title("Feature mathcing"), plt.xticks([]), plt.yticks([])
plt.subplot(235), plt.imshow(img4, cmap="gray")
plt.title("Homography"), plt.xticks([]), plt.yticks([])
plt.subplot(236), plt.imshow(img5, cmap="gray")
plt.title("WarpPerspective"), plt.xticks([]), plt.yticks([])
plt.tight_layout()
plt.show()

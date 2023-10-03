import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

# Exercise 1: Apply horisontal and vertical Sobel kernels to find edges in an image of your own choice (use the function Sobel())

filename = './sprites/aau-city-1.jpg'
img = cv.imread(filename)
assert img is not None, "File could not be read, check with os.path.exists()"

plt.subplot(221),plt.imshow(img,cmap = 'gray')
plt.title('Original image'), plt.xticks([]), plt.yticks([])

# Convert to grayscale
img_gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)

# Blur the image for better edge detection
img_blur = cv.GaussianBlur(img_gray, (3,3),0)


# Sobel Kernels
sobelx = cv.Sobel(src=img_blur, ddepth=cv.CV_64F, dx=1, dy=0, ksize=5)
sobelx = cv.Sobel(src=img_blur, ddepth=cv.CV_64F, dx=0, dy=1, ksize=5)
sobelxy = cv.Sobel(src=img_blur, ddepth=cv.CV_64F, dx=1, dy=1, ksize=5)






plt.subplot(222),plt.imshow(sobelxy, cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
# (num_rows, num_cols, index counting left to right, then top to bottom.)
plt.tight_layout()
plt.show()

cv.waitKey(0)


# Opgave 2: Test Canny edge detector on your own image. 


edges = cv.Canny(img,100,200)

plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(edges, cmap = 'gray')
plt.title('Ege Image'), plt.xticks([]), plt.yticks([])
plt.show()







import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import os

def loadImage(filename,folder, color=None):
    path = os.path.join(folder,filename)
    return cv.imread(path, color)

def getAverageBackgroundImage(files, folder):
    # Initialize variables to store accumulated pixel values
    sum_of_images = None

    # Loop through the list of images and accumulate pixel values
    for image_path in files:
        img = cv.imread(os.path.join(folder,image_path),cv.IMREAD_GRAYSCALE)
        
        # Convert the image to a floating-point format for accurate accumulation
        img_float = img.astype(np.float32)
        
        if sum_of_images is None:
            sum_of_images = img_float
        else:
            sum_of_images += img_float

    # Divide the accumulated values by the number of images to compute the average
    average_image = (sum_of_images / len(files)).astype(np.uint8)
    return average_image




# Exercise 1: Make a program to flip through the images, and display the difference to the reference frame in red.

folder = os.path.join(os.getcwd(), 'lecture3','Exercises','UCSD','Test016')

# Sorted list of images
filelist = sorted(os.listdir(folder))

# Get the first image, and use it as a reference
# refImage = loadImage(filelist[0],folder,cv.IMREAD_GRAYSCALE)

# Exercise 2: Compute an avereage background image:
# Get the 10 first images and use them to compute the average background image.
averageFiles = filelist[:10]
refImage = getAverageBackgroundImage(averageFiles,folder)


for filename in filelist:
    frame = loadImage(filename, folder)
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
     # Absolute difference between the current frame and the average background
    diff = cv.absdiff(gray, refImage)

    # Merge the difference image into the red channel
    b, g, r = cv.split(frame)
    r += diff

    # Merge the channels back to create the modified frame
    result = cv.merge((b, g, r))


    cv.imshow('Video',result)

    if cv.waitKey(1) == ord('q'):
        break

    cv.waitKey(10)

cv.destroyAllWindows()







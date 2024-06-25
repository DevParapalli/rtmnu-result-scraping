import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

# Load the image
input_image = cv.imread("image.png")

# Convert the image to grayscale
gray = cv.cvtColor(input_image, cv.COLOR_BGR2GRAY)
ret,gray = cv.threshold(gray,192,255,cv.THRESH_BINARY)
# Create a LineSegmentDetector object
detector = cv.createLineSegmentDetector()

# Detect lines in the grayscale image
lines = detector.detect(gray)[0]

# Draw the detected lines on the input image
drawn_lines = detector.drawSegments(gray.copy(), lines)

# Display the image with detected lines
cv.imshow("Lines Detected", drawn_lines)
cv.waitKey(0)
cv.destroyAllWindows()

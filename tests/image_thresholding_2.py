import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

img = cv.imread('image.png', cv.IMREAD_GRAYSCALE)
assert img is not None, "file could not be read, check with os.path.exists()"
ret,thresh1 = cv.threshold(img,192,255,cv.THRESH_BINARY)
cv.imwrite('image_thresholded.png', thresh1)
# image_blurred = cv.medianBlur(thresh1,3)
# kernel = np.zeros((3,3), np.uint8)
# kernel[1, 1] = 1 
# kernel[0, 1] = 1
# kernel[1, 0] = 1
# kernel[1, 2] = 1
# kernel[2, 1] = 1
# image_dilated = cv.dilate(thresh1, kernel, iterations=1)

def remove_pepper(image, threshold=0.7):
    # Convert image to grayscale if it's not already
    if len(image.shape) > 2:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Create a binary mask of dark pixels (pepper noise)
    pepper_pixels = (gray == 0)
    
    # Create a kernel for checking neighboring pixels
    kernel = np.ones((3,3), np.uint8)
    kernel[1,1] = 0  # Exclude the center pixel
    
    # Count white neighbors for each pixel
    white_neighbors = cv.filter2D((gray == 255).astype(np.uint8), -1, kernel)
    
    # Create a mask of pixels to change
    change_mask = pepper_pixels & (white_neighbors >= (8 * threshold))
    
    # Apply the change
    result = gray.copy()
    result[change_mask] = 255
    
    return result

def remove_isolated_black_pixels(image, connectivity=8):
    # Convert image to grayscale if it's not already
    if len(image.shape) > 2:
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Create a binary image
    _, binary = cv.threshold(gray, 1, 255, cv.THRESH_BINARY)
    
    # Find all connected components
    num_labels, labels, stats, _ = cv.connectedComponentsWithStats(binary, connectivity=connectivity)
    
    # Create output image
    output = gray.copy()
    
    # Iterate through all components (skipping the background which is label 0)
    for label in range(1, num_labels):
        if stats[label, cv.CC_STAT_AREA] <= 2:  # If the component is a single pixel
            output[labels == label] = 255  # Set this pixel to white
    
    return output

# 3 images

plt.subplot(1,2,1)
plt.imshow(thresh1,'gray',vmin=0,vmax=255)
plt.subplot(1,2,2)
plt.imshow(remove_isolated_black_pixels(thresh1),'gray',vmin=0,vmax=255)
plt.show()
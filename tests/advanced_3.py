import cv2
import numpy as np
from PIL import Image
import pytesseract
from pytesseract import Output
import os

def preprocess_image(image_path):
    # Read the image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply adaptive thresholding
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Invert the image
    inverted = cv2.bitwise_not(binary)
    
    # Apply dilation to thicken the text
    kernel = np.ones((2,2),np.uint8)
    dilated = cv2.dilate(inverted, kernel, iterations = 1)
    
    # Apply erosion to separate characters
    eroded = cv2.erode(dilated, kernel, iterations = 1)
    
    return img, gray, binary, eroded

def detect_text_regions(binary):
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours based on area and aspect ratio
    min_area = 50  # Reduced to catch smaller text
    max_aspect_ratio = 15  # Increased to catch longer words
    text_regions = []
    for c in contours:
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        aspect_ratio = max(w, h) / min(w, h)
        if area > min_area and aspect_ratio < max_aspect_ratio:
            text_regions.append((x, y, w, h))
    
    return text_regions

def ocr_text(image, regions):
    results = []
    for x, y, w, h in regions:
        roi = image[y:y+h, x:x+w]
        text = pytesseract.image_to_string(roi, config='--psm 6 --oem 3')
        if text.strip():  # Only add non-empty results
            results.append((text.strip(), (x, y, w, h)))
    return results

def save_debug_images(original, gray, binary, processed, regions, base_filename):
    cv2.imwrite(f"{base_filename}_original.png", original)
    cv2.imwrite(f"{base_filename}_gray.png", gray)
    cv2.imwrite(f"{base_filename}_binary.png", binary)
    cv2.imwrite(f"{base_filename}_processed.png", processed)
    
    # Draw rectangles around detected regions
    debug_image = original.copy()
    for x, y, w, h in regions:
        cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imwrite(f"{base_filename}_detected_regions.png", debug_image)

def image_to_text_debug(image_path):
    # Preprocess
    original, gray, binary, processed = preprocess_image(image_path)
    
    # Detect text regions
    regions = detect_text_regions(processed)
    
    # Save debug images
    base_filename = os.path.splitext(image_path)[0]
    save_debug_images(original, gray, binary, processed, regions, base_filename)
    
    # OCR on processed image
    ocr_results = ocr_text(processed, regions)
    
    return ocr_results

# Example usage
image_path = './CSE_5TH_SUM24-result_images\\648673-MIHEERA SUSHIL JADHAV.png'
results = image_to_text_debug(image_path)

# Print results
print("\nOCR Results:")
full_text = ' '.join([text for text, _ in results])
print(full_text)
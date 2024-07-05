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
    
    # Apply threshold to get image with only black and white
    _, binary = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY)
    
    # Use morphological transformations to remove small noise
    kernel = np.ones((3,3), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # Invert the image so text is white on black background
    inverted = cv2.bitwise_not(opening)
    
    return img, gray, binary, inverted

def detect_text_regions(binary):
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours based on area and aspect ratio
    min_area = 100
    max_aspect_ratio = 10
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
        text = pytesseract.image_to_string(roi, config='--psm 6')
        if text.strip():  # Only add non-empty results
            results.append((text.strip(), (x, y, w, h)))
    return results

def save_debug_images(original, gray, binary, inverted, regions, base_filename):
    cv2.imwrite(f"{base_filename}_original.png", original)
    cv2.imwrite(f"{base_filename}_gray.png", gray)
    cv2.imwrite(f"{base_filename}_binary.png", binary)
    cv2.imwrite(f"{base_filename}_inverted.png", inverted)
    
    # Draw rectangles around detected regions
    debug_image = original.copy()
    for x, y, w, h in regions:
        cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imwrite(f"{base_filename}_detected_regions.png", debug_image)

def image_to_text_debug(image_path):
    # Preprocess
    original, gray, binary, inverted = preprocess_image(image_path)
    
    # Detect text regions
    regions = detect_text_regions(inverted)
    
    # Save debug images
    base_filename = os.path.splitext(image_path)[0]
    save_debug_images(original, gray, binary, inverted, regions, base_filename)
    
    # OCR on inverted image
    ocr_results = ocr_text(inverted, regions)
    
    return ocr_results

# Example usage
image_path = './CSE_5TH_SUM24-result_images\\648673-MIHEERA SUSHIL JADHAV.png'
results = image_to_text_debug(image_path)

# Print results
print("\nOCR Results:")
for text, _ in results:
    print(text)
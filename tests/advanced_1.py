import cv2
import numpy as np
from PIL import Image
import pytesseract
from pytesseract import Output
import json
import os

def preprocess_image(image_path):
    # Read the image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Increase contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast = clahe.apply(gray)
    
    # Binarization
    _, binary = cv2.threshold(contrast, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    return img, gray, contrast, binary

def detect_text_regions(binary):
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours based on area
    min_area = 100
    text_regions = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > min_area]
    
    return text_regions

def ocr_text(image, regions):
    results = []
    for x, y, w, h in regions:
        roi = image[y:y+h, x:x+w]
        text = pytesseract.image_to_string(roi, config='--psm 6')
        results.append((text.strip(), (x, y, w, h)))
    return results

def save_debug_images(original, gray, contrast, binary, base_filename):
    cv2.imwrite(f"{base_filename}_original.png", original)
    cv2.imwrite(f"{base_filename}_gray.png", gray)
    cv2.imwrite(f"{base_filename}_contrast.png", contrast)
    cv2.imwrite(f"{base_filename}_binary.png", binary)

def image_to_text_debug(image_path):
    # Preprocess
    original, gray, contrast, binary = preprocess_image(image_path)
    
    # Save debug images
    base_filename = os.path.splitext(image_path)[0]
    save_debug_images(original, gray, contrast, binary, base_filename)
    
    # Detect text regions
    regions = detect_text_regions(binary)
    
    # Draw rectangles around detected regions
    debug_image = original.copy()
    for x, y, w, h in regions:
        cv2.rectangle(debug_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imwrite(f"{base_filename}_detected_regions.png", debug_image)
    
    # OCR on original, gray, contrast, and binary images
    ocr_results = {
        "original": ocr_text(original, regions),
        "gray": ocr_text(gray, regions),
        "contrast": ocr_text(contrast, regions),
        "binary": ocr_text(binary, regions)
    }
    
    return ocr_results

# Example usage
image_path = './CSE_5TH_SUM24-result_images\\648673-MIHEERA SUSHIL JADHAV.png'
results = image_to_text_debug(image_path)

# Print results
for image_type, texts in results.items():
    print(f"\nResults for {image_type} image:")
    for text, _ in texts:
        print(text)
import cv2
import pyperclip

def select_roi(image):
    # Select ROI
    roi = cv2.selectROI("Select ROI", image, fromCenter=False, showCrosshair=True)
    return roi

def copy_roi_to_clipboard(roi):
    # Convert ROI to string representation
    roi_string = f"x: {roi[0]}, y: {roi[1]}, width: {roi[2]}, height: {roi[3]}"
    
    # Copy to clipboard
    pyperclip.copy(roi_string)
    print("ROI coordinates copied to clipboard!")

def main():
    # Read the image
    image_path = input("Enter the path to your image: ")
    image = cv2.imread(image_path)
    
    if image is None:
        print("Error: Unable to read the image. Please check the file path.")
        return
    
    # Select ROI
    roi = select_roi(image)
    
    # Copy ROI to clipboard
    copy_roi_to_clipboard(roi)
    
    # Close all OpenCV windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
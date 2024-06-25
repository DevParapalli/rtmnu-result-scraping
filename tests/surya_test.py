from PIL import Image

from surya.ocr import run_ocr
from surya.model.detection import segformer
from surya.model.recognition.model import load_model
from surya.model.recognition.processor import load_processor

image = Image.open("image_thresholded.png")
langs = ["en"]
det_p, det_m = segformer.load_processor(), segformer.load_model()
rec_p, rec_m = load_processor(), load_model()

predictions = run_ocr([image], [langs], det_p, det_m, rec_p, rec_m)

print(predictions)
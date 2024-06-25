from doctr.models import ocr_predictor
model = ocr_predictor(pretrained=True)

from doctr.io import DocumentFile

single_img_doc = DocumentFile.from_images("path/to/your/img.jpg")

result = model(doc)

result.show()
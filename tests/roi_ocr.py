import easyocr

reader = easyocr.Reader(['en'])
result = reader.readtext('tests/test_ocr_1.png', detail=0)
print(result)
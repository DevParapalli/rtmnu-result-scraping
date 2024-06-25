# Notes

- Use <https://github.com/seatgeek/thefuzz?tab=readme-ov-file> for fuzzy matching
- 2 subintrepreters, 1 runs a localhost server for fs operations, other is the one with selenium that fetches the result and then injects a script to call the localhost with the image data
- server can be part 2, initially we should simply get details from the hall tickets


## Image Parsing ?

- Watermark makes it difficult for parsing directly, plus the quality of image is trash. use of LLMs is not viable due to the volume of images, thresholding is not valid for direct OCR, we may need to create maps for each marksheet, placing the zones manually

- <https://github.com/mindee/doctr>
- <https://huggingface.co/docs/transformers/en/model_doc/layoutlmv3>
- <https://github.com/clovaai/donut>
- <https://medium.com/@simsagues/document-information-extraction-using-ocr-and-nlp-2c3caa5a7720>
 Too much work


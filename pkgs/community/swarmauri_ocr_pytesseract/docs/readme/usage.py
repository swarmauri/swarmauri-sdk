from swarmauri_ocr_pytesseract import PytesseractOCR

ocr = PytesseractOCR(language="eng", config="--psm 6")
text = ocr.extract_text("docs/invoice.png")
print(text)

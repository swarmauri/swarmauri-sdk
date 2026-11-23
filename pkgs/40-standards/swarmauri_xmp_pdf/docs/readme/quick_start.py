from swarmauri_xmp_pdf import PDFXMP

handler = PDFXMP()

try:
    handler.remove_xmp(b"%PDF-1.7...")
except NotImplementedError:
    print("PDF XMP support will arrive in a future release.")

import easyocr
from PIL import Image
import numpy as np
import cv2

# Initialize reader (English)
reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(file):
    image = Image.open(file).convert("L")  # grayscale
    image_np = np.array(image)

    # Improve contrast (VERY IMPORTANT)
    image_np = cv2.adaptiveThreshold(
        image_np, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    result = reader.readtext(image_np, detail=0)

    # Join all detected text
    text = " ".join(result)

    return text
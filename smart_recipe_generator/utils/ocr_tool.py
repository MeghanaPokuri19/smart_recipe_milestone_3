import pytesseract
import cv2
import matplotlib.pyplot as plt
import streamlit as st

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def perform_ocr(img_path):
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary_img = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(binary_img)
    
    fig, ax = plt.subplots()
    ax.imshow(binary_img, cmap='gray')
    ax.set_title("Processed Image for OCR")
    st.pyplot(fig)  # Use Streamlit's st.pyplot to display the plot in the app

    return text

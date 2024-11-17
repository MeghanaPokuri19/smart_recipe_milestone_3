from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image

def load_image(image_path):
    img = Image.open(image_path)
    img = img.resize((256, 256))
    return img

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(128, 128))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    return img_array

'''
import gradio as gr
from tensorflow.keras.models import load_model
import numpy as np
import tensorflow as tf

model = load_model("skin_cancer_detection_model.h5")

def predict_image(image):
    img = tf.image.resize(image, (224, 224))
    img = np.expand_dims(img, axis=0)
    img = img / 255.0

    prediction = model.predict(img)
    predicted_class = np.argmax(prediction, axis=1)[0]

    class_names = ['akiec', 'bcc', 'bkl', 'df', 'nv', 'vasc', 'mel']
    disease_info = {
        'akiec': "Actinic Keratoses and Intraepithelial Carcinoma (pre-cancerous lesion)",
        'bcc': "Basal Cell Carcinoma (a common type of skin cancer)",
        'bkl': "Benign Keratosis (non-cancerous lesion)",
        'df': "Dermatofibroma (benign skin lesion)",
        'nv': "Melanocytic Nevus (a common mole)",
        'vasc': "Vascular Lesions (benign lesion of blood vessels)",
        'mel': "Melanoma (most dangerous type of skin cancer)"
    }

    return f"{class_names[predicted_class]}: {disease_info[class_names[predicted_class]]}"

# Gradio Interface
iface = gr.Interface(fn=predict_image, inputs="image", outputs="text")
iface.launch()
'''
import keras

print(keras.__version__)
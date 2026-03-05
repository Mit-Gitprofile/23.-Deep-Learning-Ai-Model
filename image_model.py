import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import (
    MobileNetV2,
    preprocess_input,
    decode_predictions
)
from tensorflow.keras.preprocessing import image

# Load lightweight pretrained model
model = MobileNetV2(weights="imagenet")

def predict_image(img):
    try:
        img = img.resize((224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        preds = model.predict(img_array)
        decoded = decode_predictions(preds, top=1)[0][0]

        label = decoded[1]
        confidence = round(float(decoded[2]) * 100, 2)

        return label, confidence

    except Exception as e:
        return None, None
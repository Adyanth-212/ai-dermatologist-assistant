
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import io, numpy as np
from PIL import Image
import tensorflow as tf

app = FastAPI(title="AI Brain")

MODEL_PATH = "ml/trained_models/efficientnet_v1/model.h5"

def load_model():
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except Exception as e:
        print("Failed to load model:", e)
        return None

model = load_model()

@app.get("/health")
def health():
    return {"status":"ok", "server":"ai_server", "model_loaded": bool(model)}

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    contents = await image.read()
    img = Image.open(io.BytesIO(contents)).convert('RGB').resize((224,224))
    arr = np.array(img)/255.0
    arr = arr.reshape((1,224,224,3))
    if model is None:
        # Dummy response fallback
        return JSONResponse(content={"label":"unknown","confidence":0.0,"warning":"model not loaded - running dummy"}, status_code=200)
    preds = model.predict(arr).tolist()
    return {"label":"class_x","confidence":0.9,"raw_preds": preds}

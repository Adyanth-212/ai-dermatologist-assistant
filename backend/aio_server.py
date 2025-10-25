
# Combined server for hackathon local failover. Runs both main logic & AI endpoints.
# You can run this with: uvicorn backend.aio_server:app --host 0.0.0.0 --port 8000

from fastapi import FastAPI, UploadFile, File
from backend.main_server import hash_report
from backend.ai_server import predict, health as ai_health

app = FastAPI(title="AIO Combined Server")

@app.get("/health")
def health():
    return {"status":"ok", "server":"aio_combined"}

# Mount or re-use functions from other modules (simple adaptation)
@app.post("/predict")
async def predict_proxy(image: UploadFile = File(...)):
    return await predict(image)

@app.post("/hash_report")
def hash_report_proxy(payload: dict):
    class R:
        def __init__(self, d):
            self.report_id = d.get("report_id","unknown")
            self.diagnosis = d.get("diagnosis",{})
    r = R(payload)
    return hash_report(r)

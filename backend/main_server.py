
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests, hashlib, json

app = FastAPI(title="Main App Server")

class Report(BaseModel):
    report_id: str
    diagnosis: dict

@app.get("/health")
def health():
    return {"status":"ok", "server":"main_server"}

@app.post("/hash_report")
def hash_report(r: Report):
    # Compute sha256 of canonical JSON
    s = json.dumps(r.dict(), sort_keys=True).encode()
    h = hashlib.sha256(s).hexdigest()
    return {"report_hash": h}

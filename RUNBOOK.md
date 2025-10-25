
# Quick Failover Runbook (1-page)

1. Start Home Cloud:
   - On AI machine (3060): `uvicorn backend.ai_server:app --host 0.0.0.0 --port 8000`
   - On Mac Mini: `uvicorn backend.main_server:app --host 0.0.0.0 --port 8001`
   - Start ngrok to expose 8001: `ngrok http 8001`

2. Hackathon Edge (AIO):
   - On teammate laptop: `bash deployment/startup_scripts/run_aio.sh`
   - Ensure model files are in `ml/trained_models/efficientnet_v1/model.h5`

3. Frontend switch:
   - Edit `frontend/public/config.json` and set `"API_BASE": "http://192.168.1.101:8000"`
   - Refresh app in browser.

4. Health checks:
   - `curl http://<host>:8000/health`
   - `curl http://<host>:8001/health`

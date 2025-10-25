
#!/bin/bash
# On the hackathon laptop: start combined AIO server
uvicorn backend.aio_server:app --host 0.0.0.0 --port 8000

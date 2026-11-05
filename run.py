import os
import sys
import uvicorn

if __name__ == "__main__":
    print("Starting Virtual Card Generator V2 (English) on http://localhost:8095 ...", flush=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8095, log_level="info")

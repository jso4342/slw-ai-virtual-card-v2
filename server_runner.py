import uvicorn
import os
import sys

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Starting uvicorn server on http://127.0.0.1:8088 ...", flush=True)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8088, reload=False, log_level="info")

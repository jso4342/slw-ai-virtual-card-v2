import subprocess
import sys
import os

log_file = open("/tmp/daemon.log", "a")
env = os.environ.copy()
env["DYLD_LIBRARY_PATH"] = "/Users/syjjang/Library/Frameworks/Python.framework/Versions/3.12/lib"

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8088"],
    stdout=log_file,
    stderr=log_file,
    env=env,
    start_new_session=True
)
print(f"Daemon process started with PID: {proc.pid}")

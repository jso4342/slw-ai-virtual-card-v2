import sys
import os
sys.path.append(os.path.abspath("../venv/lib/python3.9/site-packages"))
from google import genai
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
print(dir(client.models))

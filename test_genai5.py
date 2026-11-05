import sys
import os
sys.path.append(os.path.abspath("../venv/lib/python3.9/site-packages"))
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

print(dir(types.GenerateImagesConfig))

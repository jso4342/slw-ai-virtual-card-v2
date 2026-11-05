import os
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

memoji_prompt = "Cute Toss style 3D clay character, Apple Memoji, minimalist 3D toy, smooth glossy material, cute face, solid white background, 3D Pixar avatar render, vibrant soft lighting."

try:
    res = client.models.generate_content(
        model='gemini-3.1-flash-image',
        contents=memoji_prompt
    )
    print("Response parts:", res.candidates[0].content.parts)
    for part in res.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            print("FOUND INLINE IMAGE DATA! Length:", len(part.inline_data.data))
except Exception as e:
    print("Error:", e)

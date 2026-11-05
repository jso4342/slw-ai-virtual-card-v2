import os
import sys
import base64
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY") or "AIzaSyCePBIMv_2ak8xOgZG746At5eNFL44Tf2s"
client = genai.Client(api_key=api_key)

print("--- Testing gemini-3.1-flash-image ---", flush=True)
try:
    res = client.models.generate_content(
        model='gemini-3.1-flash-image',
        contents=['Generate a vertical 3D business card for Seoul My Soul. Standard card 54mm x 86mm.']
    )
    print("Response received:", res, flush=True)
    if res.candidates:
        for c in res.candidates:
            print("Candidate finish_reason:", c.finish_reason, flush=True)
            if c.content and c.content.parts:
                for i, p in enumerate(c.content.parts):
                    print(f"Part {i}:", p, flush=True)
                    if hasattr(p, 'inline_data') and p.inline_data:
                        print("Inline data mime:", p.inline_data.mime_type, "len:", len(p.inline_data.data), flush=True)
                    if hasattr(p, 'text') and p.text:
                        print("Text:", p.text, flush=True)
except Exception as e:
    print("ERROR:", type(e), e, flush=True)

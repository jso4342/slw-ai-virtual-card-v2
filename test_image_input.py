import os
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

memoji_3d_prompt = """
첨부된 사진을 기반으로 토스 3D 캐릭터 또는 애플 미모지와 같은 귀여운 3D 점토 캐릭터 이미지를 만들어줘. 
Official 3D Pixar Apple Memoji character render, glossy rounded 3D clay material, clean solid white background, vibrant soft lighting.
"""

# Create a small dummy image part or test image
dummy_img_bytes = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
image_part = types.Part.from_bytes(data=dummy_img_bytes, mime_type="image/png")

try:
    response = client.models.generate_content(
        model="gemini-3.1-flash-image",
        contents=[image_part, memoji_3d_prompt]
    )
    
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                mime_type = part.inline_data.mime_type or "image/png"
                b64_str = base64.b64encode(part.inline_data.data).decode('utf-8')
                print(f"SUCCESS! MIME: {mime_type}, Base64 Length: {len(b64_str)}")
except Exception as e:
    print("Error:", e)

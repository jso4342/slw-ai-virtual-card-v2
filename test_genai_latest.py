import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

memoji_3d_prompt = """
해당 첨부된 이미지를 분석하여 사진 속 인물과 닮은 토스 캐릭터 또는 애플의 미모지와 같은 3D 캐릭터 이미지를 만들어줘.
"""

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=[memoji_3d_prompt]
)
print("Response text:", response.text)

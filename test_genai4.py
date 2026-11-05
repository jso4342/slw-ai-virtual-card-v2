import sys
import os
sys.path.append(os.path.abspath("../venv/lib/python3.9/site-packages"))
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
print("Client initialized")
try:
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="첨부된 사진을 기반으로 토스 3D 캐릭터 또는 애플 미모지 같은 3D 캐릭터 이미지를 만들어줘."
    )
    print(response.text)
except Exception as e:
    print("Error:", e)

import os
import base64
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

memoji_prompt = "Cute Toss style 3D clay character, Apple Memoji, minimalist 3D toy, smooth glossy material, cute face, solid white background, 3D Pixar avatar render, vibrant soft lighting."

try:
    img_result = client.models.generate_images(
        model='gemini-3.1-flash-image',
        prompt=memoji_prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="1:1",
            output_mime_type="image/png"
        )
    )
    if img_result.generated_images:
        print("SUCCESS! Generated image bytes length:", len(img_result.generated_images[0].image.image_bytes))
    else:
        print("No image returned")
except Exception as e:
    print("Error:", e)

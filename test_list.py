import os
import sys

print("Python version:", sys.version)
from google import genai

client = genai.Client(api_key="AIzaSyCePBIMv_2ak8xOgZG746At5eNFL44Tf2s")
print("Client initialized")

try:
    models = list(client.models.list())
    print("Found models:", len(models))
    for m in models:
        print(m.name)
except Exception as e:
    print("Error listing models:", e)

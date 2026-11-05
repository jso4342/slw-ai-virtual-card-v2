import sys
import os
sys.path.append(os.path.abspath("../venv/lib/python3.9/site-packages"))
from google.genai import types
print(types.GenerateImagesConfig.model_fields)

import base64, io
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

input_path = '/Users/syjjang/.gemini/antigravity/brain/06c5cf89-34ee-4694-8231-b9e091ee4670/.user_uploaded/media__1790672244044.png'
img = Image.open(input_path).convert('RGB')

# Crop to square
w, h = img.size
min_dim = min(w, h)
left = (w - min_dim) // 2
top = (h - min_dim) // 2
img = img.crop((left, top, left + min_dim, top + min_dim)).resize((512, 512), Image.LANCZOS)

# 1. Smooth out skin heavily (Clay effect)
clay = img.filter(ImageFilter.MedianFilter(size=9))
clay = clay.filter(ImageFilter.SMOOTH_MORE)

# 2. Quantize colors (Posterize) to give it a 3D flat render look
clay = ImageOps.posterize(clay, bits=3)

# 3. Enhance color vibrancy
enhancer = ImageEnhance.Color(clay)
clay = enhancer.enhance(1.8)

# 4. Enhance contrast
contrast = ImageEnhance.Contrast(clay)
clay = contrast.enhance(1.2)

clay.save('/Users/syjjang/.gemini/antigravity/brain/06c5cf89-34ee-4694-8231-b9e091ee4670/test_toon.png')
print('Saved test_toon.png')

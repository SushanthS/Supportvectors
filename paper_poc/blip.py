from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

# Instantiate the model
image_model_id = "Salesforce/blip-image-captioning-base"
image_model = BlipForConditionalGeneration.from_pretrained(image_model_id)
processor = BlipProcessor.from_pretrained(image_model_id)

# Processing the image
file_path = "reference_image.jpeg"
file_path = "BingWallpaper.jpg"
image = Image.open(file_path).convert('RGB')
inputs = processor(image, return_tensors="pt")
out = image_model.generate(**inputs, max_new_tokens=200)

# Generate caption
caption = processor.decode(out[0], skip_special_tokens=True)

print(caption)
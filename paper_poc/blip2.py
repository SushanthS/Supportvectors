
from PIL import Image
import requests
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch

# This is a big model, hence we are pulling in the big guns
device = "cuda" if torch.cuda.is_available() else "cpu"
print(device)
# Instantiate the model
processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b", torch_dtype=torch.float16
)
model.to(device)
url = "https://llava-vl.github.io/static/images/view.jpg"
image = Image.open(requests.get(url, stream=True).raw)
file_path = "BingWallpaper.jpg"
# image = Image.open(file_path).convert('RGB')
# Process the image
inputs = processor(images=image, return_tensors="pt").to(device, torch.float16)
generated_ids = model.generate(**inputs)

# Generate the text
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True, max_new_tokens = 150)[0].strip()
print(generated_text)


# Let us try to make answer our question
# prompt = "Question: Describe the image in detail in as many words as possible. Answer:"
# inputs = processor(images=image, text=prompt, return_tensors="pt").to(device, torch.float16)

# # Generate the text
# generated_ids = model.generate(**inputs)
# generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
# print(generated_text)
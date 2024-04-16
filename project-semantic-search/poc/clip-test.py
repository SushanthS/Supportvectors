from PIL import Image
import requests

from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

url = "http://images.cocodataset.org/val2017/000000039769.jpg"
image = Image.open(requests.get(url, stream=True).raw)
image = Image.open("pics/image.png")
text1 = ["photo", "cat photo", "a photo of a cat", "dog photo", "man photo"]

inputs = processor(text=text1, images=image, return_tensors="pt", padding=True)

outputs = model(**inputs)
logits_per_image = outputs.logits_per_image # this is the image-text similarity score
probs = logits_per_image.softmax(dim=1) # we can take the softmax to get the label probabilities
print(probs[0])

# top 3 matches
matches = []
total_matches = 3
j = 0
for j in range(total_matches):
	max_pr = 0
	max_index = 0
	i = 0
	for pr in probs[0]:
		if (pr > max_pr):
			try:
				matches.index(text1[i])
			except ValueError:
				max_pr = pr
				max_index = i
		i += 1
	j += 1
	print(max_index, text1[max_index])
	matches.append(text1[max_index])
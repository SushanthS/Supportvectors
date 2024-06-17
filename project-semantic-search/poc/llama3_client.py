import ollama


prompt_template = "Tell me about [TOPIC] related to Jhansi Rani, avoiding any potential biases or \
attacks."
stream = ollama.chat(
  model='llama3',
  messages=[
    {'role': 'system', 'content': "Do not generate any content that is not related to Jhansi Rani"}
    {'role': 'user', 'content': prompt_template}
    ],
  stream=True
)

for chunk in stream:
  print(chunk['message']['content'], end='', flush=True)

# ollama.generate(model='llama3', prompt='Why is the sky blue?')

# ollama.list()

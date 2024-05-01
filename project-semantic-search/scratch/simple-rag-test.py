from transformers import pipeline

# Load the RAG model
model = pipeline("question-answering")

# Define the question and context
question = "Who is the CEO of Google?"
context = "Google is an American multinational technology company that specializes in Internet-related services and products. It is one of the world's most valuable companies. Sundar Pichai is the CEO of Google."

# Generate the answer
answer = model(question, context)

# Print the answer
print(answer)

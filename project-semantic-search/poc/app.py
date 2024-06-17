# import streamlit as st
# import pandas as pd
# import numpy as np

# st.title('Uber pickups in NYC')


"""
Topic: Jhansi Rani's public life
Restrict any other topic.
Response only about Jhansi Rani

Llama receipies.

"""
import ollama
# from llama3 import llama as llama3

# Define the prompt template
prompt_template = "Tell me about [TOPIC] related to Jhansi Rani, avoiding any potential biases or \
attacks."

# Define the allowed topics (in this case, only Jhansi Rani)
allowed_topics = ["Jhansi Rani", "Lakshmibai", "Indian history", "Warrior queen"]

# Create a LLaMA 3 model instance
ollama.
model = llama3.Model()

# Set the prompt template and allowed topics for the model
model.prompt_template = prompt_template
model.allowed_topics = allowed_topics

# Define a custom function to process user input (e.g., convert to lowercase)
def preprocess_input(input_text):
    return input_text.lower()

# Create a custom query processor that restricts queries to Jhansi Rani
def query_processor(query):
    if any(topic in query for topic in allowed_topics):
        return query
    else:
        raise ValueError("Query must be related to Jhansi Rani.")

# Set the custom query processor for the model
model.query_processor = query_processor
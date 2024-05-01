import transformers
import torch

from huggingface_hub import login
login(token="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")
#model_id = "meta-llama/Llama-2-7b-chat-hf"
model_id = "TheBloke/Llama-2-7B-GGML"
query = ""

pipeline = transformers.pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": torch.bfloat16},
    device="cuda:0",
)

messages = [
    {"role": "system", "content": "Do not generate any content that is not related to Jhansi Rani"},
    {"role": "user", "content": query},
]

prompt = pipeline.tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
)

terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]


#print(outputs[0]["generated_text"][len(prompt):])


#print(outputs)

from flask import Flask, request, render_template
#from chainlit import ChainLIT

app = Flask(__name__)

# Initialize ChainLIT model
#model = ChainLIT(model_path="path/to/model")



@app.route('/query', methods=['POST'])
def process_query():
    # Get the query from the request body
    query = request.args.get('query')

    # Preprocess the query (e.g., convert to lowercase)
    #query = query.lower()
    print(query)
    # Process the query using ChainLIT
    #result = model.process(query)
    outputs = pipeline(
        prompt,
        max_new_tokens=256,
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )
    print(outputs)
    return jsonify({'result': outputs})

if __name__ == '__main__':
    app.run(debug=True)
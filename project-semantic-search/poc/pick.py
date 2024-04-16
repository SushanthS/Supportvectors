import pickle

with open('embeddings.pkl', 'rb') as f:
    # The protocol version used is detected automatically, so we do not
    # have to specify it.
    data = pickle.load(f)
    print(type(data), data.keys())
    print(type(data["sentences"]), len(data["sentences"]))
    print(type(data["embeddings"]), len(data["embeddings"]))
    # print(data["sentences"])

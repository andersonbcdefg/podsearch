import fire
import openai
import json
from functional import seq

def get_embedding(text, api_key, model="text-embedding-ada-002"):
    openai.api_key = api_key
    return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def add_embeddings(chunk_file, api_key, model="text-embedding-ada-002"):
    with open(chunk_file, "r+") as f:
        chunks = json.load(f)
        for chunk in chunks:
            chunk["embedding"] = get_embedding(chunk["text"], api_key, model)
        with open(chunk_file + ".embeddings.json", "w+") as f:
            json.dump(chunks, f)

if __name__ == '__main__':
    fire.Fire(add_embeddings)

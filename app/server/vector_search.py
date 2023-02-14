import json
import openai
import numpy as np

class VectorDatabase:
    def __init__(self, json_file, api_key):
        openai.api_key = api_key
        self.records = json.load(open(json_file, 'r'))
        # convert embeddings to numpy array, shape (n_records, embed_dim)
        self.embs = np.array([r['embedding'] for r in self.records])
    
    def embed_query(self, query):
        response = openai.Embedding.create(
            input = [query], 
            model="text-embedding-ada-002"
        )
        return np.array(response["data"][0]['embedding'])


    def get_top_k(self, query_emb, k=10):
        scores = np.dot(self.embs, query_emb).flatten() # shape (n_records,)
        top_k = np.argsort(scores)[-k:]
        return [self.records[i] for i in top_k]

    def search(self, query, k=10):
        query_emb = self.embed_query(query)
        return self.get_top_k(query_emb, k)
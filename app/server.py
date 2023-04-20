import os

import numpy as np
import openai
from datasets import load_dataset
from fastapi import FastAPI

openai.api_key = os.environ["OPENAI_API_KEY"]

dataset = load_dataset("andersonbcdefg/tafs_index", split="train")
dataset.add_faiss_index(column="embedding")


def get_embedding(text):
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    embedding = np.array(response["data"][0]["embedding"])
    return embedding


def search(query, k=10):
    emb = get_embedding(query)
    scores, samples = dataset.get_nearest_examples("embedding", emb, k=k)
    return [
        {
            "score": float(score),
            "text": text,
            "episode_title": title,
            "episode_date": date,
            "timestamp": timestamp,
        }
        for score, text, title, date, timestamp in zip(
            scores,
            samples["text"],
            samples["episode_title"],
            samples["episode_date"],
            samples["start_time"],
        )
    ]


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/semantic-search")
def semantic_search(query: str, k: int = 10):
    return {"results": search(query, k)}

import os

import numpy as np
import openai
from datasets import load_dataset
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

openai.api_key = os.environ["OPENAI_API_KEY"]

dataset = load_dataset("andersonbcdefg/tafs_index", split="train")
dataset.add_faiss_index(column="embedding")


def is_valid(token):
    return token == "55194446-0511-4a0e-9bbe-c8013bc70050"


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
security = HTTPBearer()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/semantic-search")
def semantic_search(
    query: str,
    k: int = 10,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if not credentials.scheme == "bearer":
        raise HTTPException(status_code=403, detail="Unauthorized request.")
    token = credentials.credentials
    # Use the token to authenticate the user
    if not is_valid(token):
        raise HTTPException(status_code=403, detail="Unauthorized request." + token)
    else:
        return {"results": search(query, k)}

from typing import Union
from fastapi import FastAPI
from vector_search import VectorDatabase
app = FastAPI()

json_path = "/Users/ben/Desktop/cumtown_2_10.index.json"
api_key = input("OpenAI API key: ")
db = VectorDatabase(json_path, api_key)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/semantic-search")
def semantic_search(query: str, k: int = 10):
    return {"results": db.search(query, k)}
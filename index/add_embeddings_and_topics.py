import fire
import openai
import json
from functional import seq
import time
import pathlib

def create_prompt(text):
    prompt = f"""
    const input = "{text}";

    // Create list of main topics/people in the input string. (Max 10)
    const topics = [
    """
    return prompt.strip()

def get_topics(prompt, api_key, model="code-davinci-002"):
    openai.api_key = api_key
    response = openai.Completion.create(
        model=model,
        prompt=prompt,
        temperature=0.1,
        max_tokens=200,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["];"]
    )
    completion = response["choices"][0]["text"]
    topics = seq(completion.split(","))\
        .map(lambda x: x.strip())\
        .filter(lambda x: x != "")\
        .filter(lambda x: x[0] in ["'", '"'] and x[-1] in ["'", '"'])\
        .map(lambda x: x.strip()[1:-1]).distinct().to_list()
    return topics

def add_topics(chunk_file, api_key, model="code-davinci-002"):
    with open(chunk_file, "r+") as f:
        chunks = json.load(f)
        for chunk in chunks:
            prompt = create_prompt(chunk["text"])
            chunk["topics"] = get_topics(prompt, api_key, model)
            time.sleep(5)
        with open(chunk_file + ".topics.json", "w+") as f:
            json.dump(chunks, f)

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

def add_embeddings_and_topics(in_file, out_file, api_key):


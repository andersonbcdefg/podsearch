import fire
import openai
import json
from functional import seq
import time
import pathlib


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

def add_embeddings(chunks, api_key, model="text-embedding-ada-002"):
    
    with open(chunk_file, "r+") as f:
        chunks = json.load(f)
        for chunk in chunks:
            chunk["embedding"] = openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']
        

def add_embeddings_and_topics(in_file, out_file, api_key, rate_limit=5):
    openai.api_key = api_key
    # Open chunk file and load
    with open(in_file, "r+") as f:
        chunks = json.load(f)
        for chunk in chunks:
            # Add topics
            prompt = f"""const input = "{text}";\n\n// Create list of main topics/people in the input string. (Max 10)\n\nconst topics = ["""
            chunk["topics"] = get_topics(prompt, api_key, model)
            # Add embedding
            chunk["embedding"] = openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']
            time.sleep(rate_limit)
    with open(out_file, "w+") as f:
            json.dump(chunks, f)

def add_embeddings_and_topics_all(metadata_file, in_dir, out_dir, api_key, rate_limit=6):
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    for episode in metadata:
        in_file = pathlib.Path(f"{input_dir}/{episode['slug']}.chunks.json")
        out_file = pathlib.Path(f"{output_dir}/{episode['slug']}.index.json")
        # Make sure input file exists
        if not in_file.is_file():
            print(f"Input file {in_file} does not exist. Skipping...")
            continue
        # Make sure output file doesn't exist
        if out_file.is_file():
            print(f"Output file {out_file} already exists. Skipping...")
            continue
        print(f"Adding topics and embeddings to {in_file}, output {out_file}...")
        add_embeddings_and_topics(in_file, out_file, api_key, rate_limit)



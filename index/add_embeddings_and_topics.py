import json
import pathlib
import time

import openai
from functional import seq

# def get_topics(inputs, api_key, model="code-davinci-002"):
#     prompts = seq(inputs).map(
#         lambda x: f"""const input = "{x}";\n\n// Create list of main topics/"""
#         + """people in the input string. (Max 10)\n\nconst topics = ["""
#     )
#     openai.api_key = api_key
#     response = openai.Completion.create(
#         model=model,
#         prompt=list(prompts),
#         temperature=0.1,
#         max_tokens=200,
#         top_p=1.0,
#         frequency_penalty=0.0,
#         presence_penalty=0.0,
#         stop=["];"],
#     )
#     completions = [response["choices"][i]["text"] for i in range(len(inputs))]
#     topic_lists = (
#         seq(completions)
#         .map(
#             lambda completion: seq(completion.split(","))
#             .map(lambda x: x.strip())
#             .filter(lambda x: x != "")
#             .filter(lambda x: x[0] in ["'", '"'] and x[-1] in ["'", '"'])
#             .map(lambda x: x.strip()[1:-1])
#             .distinct()
#             .to_list()
#         )
#         .to_list()
#     )
#     return topic_lists


def add_embeddings(in_file, out_file, api_key, rate_limit=5):
    openai.api_key = api_key
    # Open chunk file and load
    with open(in_file, "r+") as f:
        chunks = json.load(f)
        out_chunks = []
        for i in range(0, len(chunks), 20):
            chunk_slice = chunks[i : i + 20]
            inputs = [chunk["text"] for chunk in chunk_slice]

            # Add embedding
            response = openai.Embedding.create(
                input=inputs, model="text-embedding-ada-002"
            )
            embeddings = (
                seq(response["data"])
                .sorted(key=lambda x: x["index"])
                .map(lambda x: x["embedding"])
                .to_list()
            )
            for i, chunk in enumerate(chunk_slice):
                chunk["embedding"] = embeddings[i]
                out_chunks.append(chunk)
            time.sleep(rate_limit)
    with open(out_file, "w+") as f:
        json.dump(out_chunks, f)


def add_embeddings_all(metadata_file, input_dir, output_dir, api_key, rate_limit=6):
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
        add_embeddings(in_file, out_file, api_key, rate_limit)

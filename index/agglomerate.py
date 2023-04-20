import json
import math
import pathlib

import fire


def agglomerate(input_file, output_file, chunk_length=180, overlap=60):
    mini_chunk_length = math.gcd(chunk_length, overlap)
    assert (
        mini_chunk_length > 1
    ), "You don't actually want the moving window to be 1 second long..."
    with open(input_file, "r+") as f:
        data = json.load(f)
    current_mini_chunk = {"start_time": 0, "end_time": 0, "text": ""}
    mini_chunks = []
    for segment in data:
        if current_mini_chunk["text"] == "":
            current_mini_chunk["start_time"] = segment["start"]
        current_mini_chunk["end_time"] = segment["end"]
        current_mini_chunk["text"] += segment["text"]
        curr_length = current_mini_chunk["end_time"] - current_mini_chunk["start_time"]
        if curr_length >= mini_chunk_length:
            # This way it can't be too long, even if no punctuation is found.
            # We eventually cut run-on sentences.
            if (
                current_mini_chunk["text"][-1] in ".!?"
                or curr_length >= mini_chunk_length * 1.5
            ):
                mini_chunks.append(current_mini_chunk)
                current_mini_chunk = {"start_time": 0, "end_time": 0, "text": ""}
    if current_mini_chunk["text"] != "":
        mini_chunks.append(current_mini_chunk)

    num_mini_chunks_per_chunk = chunk_length // mini_chunk_length
    num_mini_chunks_per_overlap = overlap // mini_chunk_length
    chunks = []
    current_mini_chunk = 0
    current_chunk = {"start_time": 0, "end_time": 0, "text": ""}
    num_mini_chunks_added = 0
    while current_mini_chunk < len(mini_chunks):
        # Add the mini chunk to the chunk
        if current_chunk["text"] == "":
            current_chunk["start_time"] = mini_chunks[current_mini_chunk]["start_time"]
        current_chunk["text"] += mini_chunks[current_mini_chunk]["text"]
        current_chunk["end_time"] = mini_chunks[current_mini_chunk]["end_time"]
        num_mini_chunks_added += 1
        current_mini_chunk += 1

        # If we've added enough mini chunks, add the chunk to the list of chunks
        if num_mini_chunks_added == num_mini_chunks_per_chunk:
            current_chunk["text"] = current_chunk["text"].strip()
            chunks.append(current_chunk)
            current_chunk = {"start_time": 0, "end_time": 0, "text": ""}
            num_mini_chunks_added = 0
            # Backtrack to the beginning of the overlap to start the next chunk
            current_mini_chunk -= num_mini_chunks_per_overlap

    if (
        current_chunk["text"] != ""
        and current_chunk["end_time"] != chunks[-1]["end_time"]
    ):
        current_chunk["text"] = current_chunk["text"].strip()
        chunks.append(current_chunk)

    with open(output_file, "w+") as f:
        json.dump(chunks, f)


def agglomerate_all(metadata_file, input_dir, output_dir, chunk_length=180, overlap=60):
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    for episode in metadata:
        in_file = pathlib.Path(f"{input_dir}/{episode['slug']}.segments.json")
        out_file = pathlib.Path(f"{output_dir}/{episode['slug']}.chunks.json")
        # Make sure input file exists
        if not in_file.is_file():
            print(f"Input file {in_file} does not exist. Skipping...")
            continue
        # Make sure output file doesn't exist
        if out_file.is_file():
            print(f"Output file {out_file} already exists. Skipping...")
            continue
        print(f"Agglomerating {in_file}, output {out_file}...")
        agglomerate(
            f"{input_dir}/{episode['slug']}.segments.json",
            f"{output_dir}/{episode['slug']}.chunks.json",
            chunk_length,
            overlap,
        )


if __name__ == "__main__":
    fire.Fire(agglomerate)

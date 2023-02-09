import json
import pathlib
import fire
from functional import seq

def build_index(metadata_file, input_dir, output_path):
    output_file = pathlib.Path(output_path)
    if output_file.exists():
        print(f"Output file {output_file} already exists, skipping.")
        return
    index = []
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    for episode in metadata:
        in_file = pathlib.Path(f"{input_dir}/{episode['slug']}.index.json")
        # Make sure input file exists
        if not in_file.is_file():
            print(f"Input file {in_file} does not exist, skipping")
            continue
        # Read episode with topics and embeddings
        with open(in_file, "r") as f:
            episode_index = json.load(f)
        # Add episode metadata
        for chunk in episode_index:
            chunk["episode"] = episode["slug"]
            chunk["episode_title"] = episode["title"]
            chunk["episode_date"] = episode["date"]
        index.extend(episode_index)
    # Write index to file
    with open(output_path, "w+") as f:
        json.dump(index, f)        
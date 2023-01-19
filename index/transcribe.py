from functional import seq
import fire
import whisper
import json
import pathlib
import tqdm

def transcribe_all(metadata_file, input_dir, output_dir, model_name="small.en", audio_format="mp3"):
    print(f"Loading model {model_name}...")
    model = whisper.load_model(model_name)
    print("Model loaded. Transcribing...")
    with open(metadata_file, "r") as f:
        metadata = json.load(f)
    for episode in metadata:
        episode_file = pathlib.Path(input_dir) / f"{episode['slug']}.{audio_format}"
        # Make sure the file exists
        if not episode_file.is_file():
            print(f"Skipping {episode['slug']} because it doesn't exist.")
            continue
        # Check if the output file already exists
        output_file = pathlib.Path(output_dir) / f"{episode['slug']}.segments.json"
        if output_file.is_file():
            print(f"Skipping {episode['slug']} because it has already been transcribed.")
            continue
        print(f"Transcribing {episode_file} into {output_dir}...")
        try:
            result = model.transcribe(str(episode_file))
            output = seq(result["segments"]).map(lambda x: {
                "text": x["text"], 
                "start": x["start"], 
                "end": x["end"]
            }).to_list()
            with open(output_file, "w+") as f:
                json.dump(output, f)
        except Exception as e:
            print(f"Failed to transcribe {episode_file}, skipping. ({e})")


if __name__ == '__main__':
    fire.Fire(transcribe_all)
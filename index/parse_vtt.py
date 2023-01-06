import sys
import re
import json
import openai
from functional import seq
openai.api_key = "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"

response = openai.Embedding.create(
  input="porcine pals say",
  model="text-embedding-ada-002"
)

def get_embedding(text, model="text-embedding-ada-002"):
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def parse_vtt(vtt_file, chunk_duration):
  # Initialize variables
  start_time = 0
  end_time = 0
  text = ""
  chunks = []

  # Open the .vtt file and read the lines
  with open(vtt_file, "r") as f:
    # Iterate over the lines
    while True:
      line = f.readline()
      if not line:
        # Add the final chunk to the list
        chunks.append({"start_time": start_time, "end_time": end_time, "text": text})
        break

      # Check if the line is a timecode
      if "-->" in line:
        line_start_time, line_end_time = line.split(" --> ")
        if text == "":
          # If the text is empty, this is the first timecode
          start_time = timecode_to_seconds(line_start_time)
        
        # Update the end time
        end_time = timecode_to_seconds(line_end_time)

        # Get text from the following line
        new_text = f.readline().strip()
        text += " " + new_text

        # Check if we have reached the end of a chunk
        if end_time - start_time >= chunk_duration and text[-1] in ".!?":
          # Add the current chunk to the list
          chunks.append({"start_time": start_time, "end_time": end_time, "text": text})

          # Reset the start and end times and the text
          start_time = 0
          end_time = 0
          text = ""
      else:
        continue              

  return chunks

def timecode_to_seconds(timecode):
  # Extract the hours, minutes, and seconds from the timecode
  pieces = timecode.split(":")
  if len(pieces) == 2:
    hours = "0"
    minutes, seconds = pieces
  else:
    hours, minutes, seconds = pieces
  seconds, milliseconds = seconds.split(".")

  # Convert the timecode to seconds
  seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
  return seconds


if __name__ == "__main__":
    # Get the .vtt file from the command line
    vtt_file = sys.argv[1]
    
    # Parse the .vtt file
    chunks = parse_vtt(vtt_file, 180)
    with_embeddings = seq(chunks).map(lambda x: {**x, "embedding": get_embedding(x["text"])})

    # Get the output file from the command line
    output_file = sys.argv[2]
    
    # Write the chunks to the output file as JSON
    with open(output_file, "w") as f:
        json.dump(list(with_embeddings), f)

    print("Done! Wrote {} chunks to {}".format(len(chunks), output_file))
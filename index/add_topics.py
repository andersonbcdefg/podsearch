import fire
import openai
import json
from functional import seq
import time

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
    print(completion)
    topics = seq(completion.split(","))\
        .map(lambda x: x.strip())\
        .filter(lambda x: x != "")\
        .filter(lambda x: x[0] in ["'", '"'] and x[-1] in ["'", '"'])\
        .map(lambda x: x.strip()[1:-1]).distinct().to_list()
    print(topics)
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

if __name__ == '__main__':
    fire.Fire(add_topics)
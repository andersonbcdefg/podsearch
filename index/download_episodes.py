import fire
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import json
from functional import seq
from slugify import slugify
from datetime import datetime
from dateutil.parser import parse
import pathlib

def download(xml, show_title, output_dir=".", test=False):
	feed = open(xml, 'r+')
	soup = BeautifulSoup(feed, 'xml')
	items = soup.find_all('item')
	links = [i.find('enclosure')['url'] for i in items]
	titles = seq([i.find('title').string for i in items])\
		.map(lambda x: x.replace('/', '_')).to_list()
	slugs = seq(titles).map(lambda x: slugify(x)).to_list()
	dates = seq([i.find('pubDate').string for i in items])\
		.map(lambda x: parse(x).strftime("%Y-%m-%d")).to_list()
	print(f"Downloading {len(links)} episodes into {output_dir}")
	for i in tqdm(range(len(links))):
		if not test:
			res = requests.get(links[i])
			file_path = pathlib.Path(output_dir) / f"{slugs[i]}.mp3"
			with open(file_path, "wb+") as f:
				f.write(res.content)
	metadata = [
		{
			"title": titles[i],
			"slug": slugs[i],
			"date": dates[i],
			"link": links[i]
		} for i in range(len(links))
	]
	metadata_file = pathlib.Path(output_dir) / f"{show_title}.metadata.json"
	with open(metadata_file, "w+") as f:
		json.dump(metadata, f)
		

if __name__ == '__main__':
	fire.Fire(download)
import os
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

def download(xml_file, metadata_file, output_dir=".", test=False):
	feed = open(xml_file, 'r+')
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
		# if episode already exists, skip
		file_path = pathlib.Path(output_dir) / f"{slugs[i]}.mp3"
		if os.path.isfile(file_path):
			print(f"Skipping episode {slugs[i]} because it already exists.")
			continue
		if not test:
			try:
				res = requests.get(links[i])
				with open(file_path, "wb+") as f:
					f.write(res.content)
			except Exception as e:
				print(f"Failed to download episode {titles[i]}: {e}")
	metadata = [
		{
			"title": titles[i],
			"slug": slugs[i],
			"date": dates[i],
			"link": links[i]
		} for i in range(len(links))
	]
	with open(metadata_file, "w+") as f:
		json.dump(metadata, f)
		

if __name__ == '__main__':
	fire.Fire(download)
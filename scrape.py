import requests
from bs4 import BeautifulSoup
import os.path
import json
from pySmartDL import SmartDL
import logging
import sys

# baseURL = 'https://oshoworld.com/audio-discourse-hindi-'
baseURL = 'https://oshoworld.com/osho-audio-discourse-english-'

download_dir = 'downloads/English'
cache_dir = 'cache'

if not os.path.exists(download_dir):
	os.makedirs(download_dir)

if not os.path.exists(cache_dir):
	os.makedirs(cache_dir)

headers = {
	 "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
}

alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

def cached_get(url: str, is_json=False):
	file_name = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
	if file_name.startswith('?'):
		file_name = file_name[1:]
	file_path = os.path.join(os.getcwd(), cache_dir, file_name + '.json' if is_json else file_name + '.html')

	if os.path.isfile(path=file_path):
		with open(file_path, 'rt', encoding='utf-8') as f:
			if is_json:
				return json.load(f)
			else:
				return f.read()
	else:
		req = requests.get(url, headers=headers)
		content = req.json() if is_json else requests.get(url, headers=headers).text
		with open(file_path, mode='wt', encoding='utf-8') as f:
			if is_json:
				f.write(json.dumps(content))
			else:
				f.write(content)
		return content

def download_discourse(url: str, base_dir: str):
	logger.info('Finding tracks for Discourse ' + url + '...')
	try:
		soup = BeautifulSoup(cached_get(url), 'html.parser')
		discourse = soup.find('meta', attrs={'property': 'og:title'})['content'].split(' # ')[0]
		discourse_dir = base_dir + '/' + discourse
		
		if not os.path.exists(discourse_dir):
			os.makedirs(discourse_dir)

		audio_igniter = soup.find('div', attrs={'class': 'audioigniter-root'})['data-tracks-url']
		tracks = cached_get(url=audio_igniter, is_json=True)
		for track in tracks:
			file_name = track['downloadFilename'] or track['title'] + '.mp3'
			download_url = track['downloadUrl'] or track['audio']
			if os.path.isfile(path=discourse_dir + '/' + file_name):
				logger.info('Track ' + track['title'] + ' already exists. Skipping...')
				continue

			logger.info('>> Downloading ' + file_name + ' : ' + download_url)
			dl = SmartDL(download_url, dest=discourse_dir + '/' + file_name, timeout=600)
			try:
				dl.start()
				if dl.isFinished() and dl.isSuccessful():
					logger.info('>> Downloaded ' + file_name)
				else:
					logger.error('>> Failed to download ' + file_name)
			except Exception as e:
				logger.exception(e)
				continue
	except Exception as e:
		logger.exception(e)
	

for alphabet in alphabets:
	dir_alpha = download_dir + '/' + alphabet

	if not os.path.exists(dir_alpha):
		os.makedirs(dir_alpha)

	logger.info('Finding discourses with ' + alphabet.capitalize() + '...')
	url = baseURL + alphabet + '/'
	soup = BeautifulSoup(cached_get(url), 'html.parser')
	discourses = soup.find_all('a', string="Play & Download", href=True)
	discourse_links = [discourse['href'] for discourse in discourses]

	for discourse in discourse_links:
		download_discourse(discourse, dir_alpha)

logger.info('>>>> Completed all downloads! <<<<')

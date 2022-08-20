import requests
from bs4 import BeautifulSoup
import os.path
import json
from pySmartDL import SmartDL

download_dir = 'downloads'
cache_dir = 'cache'

if not os.path.exists(download_dir):
	os.makedirs(download_dir)

if not os.path.exists(cache_dir):
	os.makedirs(cache_dir)

headers = {
	 "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
}

baseURL = 'https://oshoworld.com/audio-discourse-hindi-'

alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def cached_get(url: str, is_json=False):
	fileName = url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
	if fileName.startswith('?'):
		fileName = fileName[1:]
	filePath = os.path.join(os.getcwd(), cache_dir, fileName + '.json' if is_json else fileName + '.html')

	if os.path.isfile(path=filePath):
		if is_json:
			with open(filePath, 'r') as f:
				return json.load(f)
		else:
			return open(filePath, mode='rt', encoding='utf-8').read()
	else:
		req = requests.get(url, headers=headers)
		content = req.json() if json else requests.get(url, headers=headers).text
		with open(filePath, mode='wt', encoding='utf-8') as f:
			if is_json:
				f.write(json.dumps(content))
			else:
				f.write(content)
		return content

def download_discourse(url: str, base_dir: str):
	print('Finding tracks for Discourse ' + url + '...')
	soup = BeautifulSoup(cached_get(url), 'html.parser')
	discourse = soup.find('meta', attrs={'property': 'og:title'})['content'].split(' # ')[0]
	discourse_dir = base_dir + '/' + discourse
	
	if not os.path.exists(discourse_dir):
		os.makedirs(discourse_dir)

	audio_igniter = soup.find('div', attrs={'class': 'audioigniter-root'})['data-tracks-url']
	tracks = cached_get(url=audio_igniter, is_json=True)
	for track in tracks:
		fileName = track['downloadFilename'] or track['title'] + '.mp3'
		downloadURL = track['downloadUrl'] or track['audio']
		if os.path.isfile(path=discourse_dir + '/' + fileName):
			print('Track ' + track['title'] + ' already exists. Skipping...')
			continue

		print('>> Downloading ' + fileName + ' : ' + downloadURL)
		dl = SmartDL(downloadURL, dest=discourse_dir + '/' + fileName, timeout=600)
		dl.start()
		if dl.isFinished() and dl.isSuccessful():
			print('>> Downloaded ' + fileName)
		else:
			print('>> Failed to download ' + fileName)
	

for alphabet in alphabets:
	dir_alpha = download_dir + '/' + alphabet

	if not os.path.exists(dir_alpha):
		os.makedirs(dir_alpha)

	print('Finding discourses with ' + alphabet.capitalize() + '...')
	url = baseURL + alphabet + '/'
	soup = BeautifulSoup(cached_get(url), 'html.parser')
	discourses = soup.find_all('a', string="Play & Download", href=True)
	discourse_links = [discourse['href'] for discourse in discourses]

	for discourse in discourse_links:
		download_discourse(discourse, dir_alpha)

print('>>>> Completed all downloads! <<<<')

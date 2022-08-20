import requests
from bs4 import BeautifulSoup
import os.path
from pySmartDL import SmartDL

base_dir = 'downloads'

if not os.path.exists(base_dir):
	os.makedirs(base_dir)

headers = {
	 "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0"
}

baseURL = 'https://oshoworld.com/audio-discourse-hindi-'

alphabets = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def download_discourse(url: str, base_dir: str):
	print('Finding tracks for Discourse ' + url + '...')
	soup = BeautifulSoup((requests.get(url, headers=headers).content), 'html.parser')
	discourse = soup.find('meta', attrs={'property': 'og:title'})['content'].split(' # ')[0]
	discourse_dir = base_dir + '/' + discourse
	
	if not os.path.exists(discourse_dir):
		os.makedirs(discourse_dir)

	audio_igniter = soup.find('div', attrs={'class': 'audioigniter-root'})['data-tracks-url']
	tracks = requests.get(audio_igniter, headers=headers).json()
	for track in tracks:
		if os.path.isfile(path=discourse_dir + '/' + track['downloadFilename']):
			print('Track ' + track['title'] + ' already exists. Skipping...')
			continue

		print('>> Downloading ' + track['downloadFilename'] + ' : ' + track['downloadUrl'])
		dl = SmartDL(track['downloadUrl'], dest=discourse_dir + '/' + track['downloadFilename'], timeout=600)
		dl.start()
		if dl.isFinished() and dl.isSuccessful():
			print('>> Downloaded ' + track['downloadFilename'])
		else:
			print('>> Failed to download ' + track['downloadFilename'])
	

for alphabet in alphabets:
	dir_alpha = base_dir + '/' + alphabet
	if not os.path.exists(dir_alpha):
		os.makedirs(dir_alpha)

	file_path = os.path.join(os.getcwd(), base_dir, alphabet + '.txt')
	
	if os.path.isfile(file_path):
		with open(file_path, mode='r', encoding='utf-8') as file:
			print('Found discourses with ' + alphabet.capitalize() + ' in: ' + alphabet + '.txt \n')
			for line in file:
				download_discourse(line, dir_alpha)

	else:
		print('Finding discourses with ' + alphabet.capitalize() + '...')
		url = baseURL + alphabet + '/'
		soup = BeautifulSoup((requests.get(url, headers=headers).content), 'html.parser')
		discourses = soup.find_all('a', string="Play & Download", href=True)
		discourse_links = [discourse['href'] for discourse in discourses]

		with open(file_path, mode='wt', encoding='utf-8') as file:
			file.write('\n'.join(discourse_links))

		for discourse in discourse_links:
			download_discourse(discourse, dir_alpha)

print('>>>> Completed all downloads! <<<<')

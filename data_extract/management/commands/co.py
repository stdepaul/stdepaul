import requests
import re 
import json
import math

from django.core.management.base import BaseCommand

from bs4 import BeautifulSoup as Soup

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.template.defaultfilters import slugify

from wiki.models import WikiEntry

from root_app.views import search_city
# search_city takes city as input, not address

from django.contrib.auth.models import User
import requests
import signal

class timeout:
	def __init__(self, seconds=1, error_message='Timeout'):
	    self.seconds = seconds
	    self.error_message = error_message
	def handle_timeout(self, signum, frame):
	    raise TimeoutError(self.error_message)
	def __enter__(self):
	    signal.signal(signal.SIGALRM, self.handle_timeout)
	    signal.alarm(self.seconds)
	def __exit__(self, type, value, traceback):
	    signal.alarm(0)

class Command(BaseCommand):
	help = 'Extract data from 211texas.org'
	page = 1
	terms = {
		'food' : 'food',
		'housing': 'rent_utilities',
	}

	def start(self):

		
		while True:
			self.page += 1 
			for term in self.terms.keys():
				cookies = {
				    '_ga': 'GA1.2.1538355703.1673311920',
				    '_gid': 'GA1.2.1337310564.1674434619',
				    '_gat_gtag_UA_89827351_1': '1',
				    '_gali': 'searchForm',
				    '_united-way-211_session': 'dmt5MFBadUpPbGVFbDROaFUwNWw3N2lxU3NlYXZOSG4yNW1XbnhZMFNsVXVyNTV1VEdVR3RrUENjTFZBNnNWY0wwK2pkNG96aFB1YlpobEtVWjBDK2I1Z2llZDNaaEdwYlE5cWZOTW1yc1ZHUEY5dFFtYldlbWN3dXpPR0w0ZTZidXRVaVhzOWxHMDBrbS9BSG41Z0Z3PT0tLUpKNisrQXU5STlNbkF0elcrYTVuNVE9PQ%3D%3D--3c5d1b5f6534d341045ad1af67cda2844b207202',
				}

				headers = {
				    'Accept': 'application/json, text/javascript, */*; q=0.01',
				    'Accept-Language': 'en-US,en;q=0.9',
				    'Connection': 'keep-alive',
				    'Content-Type': 'application/json',
				    'Origin': 'https://search.211colorado.org',
				    'Referer': f'https://search.211colorado.org/search?terms={term}&page={self.page}&location=Colorado&service_area=colorado',
				    'Sec-Fetch-Dest': 'empty',
				    'Sec-Fetch-Mode': 'cors',
				    'Sec-Fetch-Site': 'same-origin',
				    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
				    'X-CSRF-Token': 'Gb-ZxjbhSnq7mMZjQyBmvJZ-byCr8dpjcJhqOiHCiHpRkHRDyTB39_3YE4JPNAVby99Xd_z0FRwkICP9rRG-wQ',
				    'X-Requested-With': 'XMLHttpRequest',
				    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
				    'sec-ch-ua-mobile': '?0',
				    'sec-ch-ua-platform': '"Linux"',
				}

				json_data = {
				    'page': self.page,
				    'per_page': 25,
				    'location': 'Colorado',
				    'service_area': 'colorado',
				    'terms': [
				        term
				    ],
				    'coords': {
				        'lng': -105.7820674,
				        'lat': 39.5500507,
				    },
				}

				response = requests.post('https://search.211colorado.org/search', cookies=cookies, headers=headers, json=json_data)

				data = json.loads(response.text)

				results = data['results']

				total_results = data['total_results']

				if self.page > math.ceil(total_results / 25):
					return False

				for result in results:


					if result['address_2']:
						address_2 = result['address_2']
					else:
						address_2 = ''
					address = f"{result['address_1']} {address_2}, {result['city']}, {result['state']} {result['postal_code']}"

					try:
						location = search_city(result['city'], 'co')
					except Exception as e:
						print(e)
						continue
					if result['website']:
						url = result['website']

						no_website = False
						website = url if "://" in url else "http://" + url

					else:

						no_website = True
						website = None
				
					has_image = False

					if not no_website:
						try:
							with timeout(seconds=10):
								r = requests.get(website)
								soup = Soup(r.content, 'html.parser')
								images = [item['content']
										  for item in soup.findAll("meta", {'property': "og:image"})]

								img_temp = NamedTemporaryFile(delete=True)
								img_temp.write(requests.get(images[0]).content)
								img_temp.flush()

								img_filetype = images[0].split('.')[-1].split('?')[0]

								has_image = True

						except Exception as e:
							print(e)

					try:

						if result['name'] != '':
							w = WikiEntry.objects.create(	
								title=result['agency_name'],
								description=result['description'],
								address=address,
								hours_of_operation=result['hours'],
								website=website,
								helper_type=self.terms[term],
								location=location,
								slug=slugify(result['agency_name'])[:50],
								phone_number=result['agency_phones']['phone_1'],
								is_verified=True,
								email=result['account_owner_email'],
							)

							if has_image:
								w.thumbnail.save(f"{slugify(result['name'])}-thumbnail.{img_filetype}", img_temp)

							print(f"added {result['agency_name']}")
					except Exception as e:
						print(e)

	def handle(self, *args, **kwargs):
		self.start()
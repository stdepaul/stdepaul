import time
import requests
import re 

from django.core.management.base import BaseCommand

from bs4 import BeautifulSoup as Soup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.template.defaultfilters import slugify

from wiki.models import WikiEntry

from root_app.views import search_city

import os
import json
from django.conf import settings

import signal

from urllib.parse import urlparse
from urllib.parse import parse_qs

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
	
	help = 'Extract data from ca211.org'

	initial_url = 'http://211ca.org'

	categories = [
		('food', 'food'),
		('utility-assistance', 'rent_utilities'),
		('housing', 'rent_utilities'),
	]
	
	region_code = 'ca'
	links = []
	next_pages = []
	initial_links_to_follow = []
	search_terms = []
	info_page_links = []
	ids = []
	def build_link(self, url, loc):
		return f'{url}&location={loc}'

	def start(self):

		options = Options()
		#options.headless = True

		profile = webdriver.FirefoxProfile()

		self.driver = webdriver.Firefox(firefox_profile=profile, options=options)

		self.driver.get(self.initial_url)
		"""
		for category in self.categories:
			category_element = self.driver.find_element_by_css_selector(f'#{category[0]}')
			category_element.click()
			time.sleep(1)
			
			category_element_parent_class = category_element.find_element_by_xpath('..').get_attribute('class')
			wrapper_subnav_element = self.driver.find_element_by_xpath(
				f'//*[@class="{category_element_parent_class}"]/following-sibling::div')
			menu_items = wrapper_subnav_element.find_elements_by_css_selector('.menuitem')

			for link_in_list in menu_items:
				self.links.append({
					'href': link_in_list.get_attribute('href'),
					'helper_type': category[1]
				})
		"""

		self.links = [
			#{
			#	'href': 'https://www.211ca.org/search?search=food',
			#	'helper_type': 'food',
			#},
			{
				'href': 'https://www.211ca.org/search?search=housing',
				'helper_type': 'rent_utilities',
			}, {
				'href': 'https://www.211ca.org/search?search=utility-assistance',
				'helper_type': 'rent_utilities'
			}
		]

		path = os.path.join(
			os.path.dirname(
				settings.BASE_DIR), 'data_extract/management/commands/ca/data.json')

		with open(path, 'rb') as f:
			self.cities = [city['name'] for city in json.loads(f.read())[:50]]

		for link in self.links:
			"""
			for city in self.cities:
				print('city', city)
				
			"""
			city = 'San Diego'
			self.info_page_links = []
			self.get_pages(self.build_link(link['href'], city), link['helper_type'])

		self.driver.quit()

	def follow_page_link(self, link):

		# appends page links to self.info_page_links

		print(f'following link {link}')
		self.driver.get(link)
		helpers = self.driver.find_elements_by_css_selector('.uk-padding-small-left')
		for helper in helpers:
			href_element = helper.find_element_by_css_selector(".gtm-card-title")
			href = href_element.get_attribute('href')

			parsed_href = urlparse(href)
			_id = parse_qs(parsed_href.query)['idServiceAtLocation'][0]
			if _id not in self.ids:
				self.info_page_links.append(href)
				self.ids.append(_id)
				print(f'added {href}')
		
	def get_pages(self, link, helper_type):

		# gets links in map pages

		self.driver.get(link)

		try:
			page_count = int(self.driver.find_element_by_xpath(
					f'//*[@class="uk-margin-auto-left"]/preceding-sibling::li[1]').text)
		except Exception as e:
			time.sleep(180)
			self.driver.get(link)
			page_count = int(self.driver.find_element_by_xpath(
					f'//*[@class="uk-margin-auto-left"]/preceding-sibling::li[1]').text)

		print('page count', page_count)

		for i in range(page_count):
			print('i', i)
			if i == 0:
				first_link = self.driver.current_url
				self.follow_page_link(first_link)

			next_page_element = self.driver.find_element_by_css_selector('.uk-margin-auto-left')
			next_page_link = next_page_element.find_element_by_tag_name('a').get_attribute('href')
			self.follow_page_link(next_page_link)

		self.get_data(helper_type)

	def parse_li(self, li_elements):

		obj = {
			'description': '',
			'website': None,
			'email': None,
			'phone': None,
			'hours': None,
		}

		for li_element in li_elements:

			if 'Description' in li_element.text:
				obj['description'] = li_element.text.split('Description: ')[-1]

			if 'Website' in li_element.text:
				try:
					obj['website'] = li_element.find_element_by_tag_name('a').get_attribute('href')
				except Exception as e:
					print(e)

			if 'Email' in li_element.text:
				obj['email'] = li_element.text.split('Email: ')[-1]

			if 'Phone' in li_element.text:
				obj['phone'] = li_element.text.split('Phone(s): ')[-1]

			if 'Hours' in li_element.text:
				obj['hours'] = li_element.text.split('Hours: ')[-1]

			if 'Eligibility' in li_element.text:
				obj['description'] += f"\n\n{li_element.text}"

			if 'Requirements' in li_element.text:
				obj['description'] += f"\n\n{li_element.text}"

		return obj

	def get_address(self, right_li_elements):

		address = None

		for right_li_element in right_li_elements:
			if 'Physical Address' in right_li_element.text:
				address = right_li_element.text.split('Physical Address: ')[-1]

		return address

	def get_data(self, helper_type):



		for i, link in enumerate(self.info_page_links):

			try:
				self.driver.get(link)

			
				title = self.driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div/div/div/div[2]/p').text.split('Organization Name: ')[-1]

			except Exception as e:
				time.sleep(180)
				continue
			li_elements = self.driver.find_elements_by_css_selector('.description > li')

			data_obj = self.parse_li(li_elements)


			address = self.get_address(self.driver.find_elements_by_css_selector('.locations-list > li'))

			print(f' website {data_obj["website"]}')

			if data_obj['website']:

				no_website = False
				website = data_obj['website']

			else:

				no_website = True
				website = None
				

			has_image = False

			if not no_website:
				try:
					with timeout(seconds=10):
						print(website)
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

			helper_type = helper_type
			print(address)
			loc_search_str =  address.split(',')[1].strip()
			location = search_city(loc_search_str, self.region_code)

			try:
				print('LINK', link)
				print(f'LINK {i+1} of {len(self.info_page_links)}')
				print("         ")

				if title != '':
					w = WikiEntry.objects.create(
						title=title,
						description=data_obj['description'],
						address=address,
						hours_of_operation=data_obj['hours'],
						website=data_obj['website'],
						helper_type=helper_type,
						location=location,
						slug=slugify(title)[:50],
						phone_number=data_obj['phone'],
						is_verified=True,
						email=data_obj['email'],
					)

					print(f'added {title}')

					if has_image:
						w.thumbnail.save(f"{slugify(title)}-thumbnail.{img_filetype}", img_temp)

			except Exception as e:
				print(e)

	def handle(self, *args, **kwargs):
		self.start()
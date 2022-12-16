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

from django.contrib.auth.models import User


class Command(BaseCommand):
	help = 'Extract data from pa211.org'
	urls = {
		'https://www.pa211.org/get-help/housing-shelter': {
			'exclude': [
				'Home Purchase and Rental',
				'Subsidized Housing',
				'Home Improvement',
				'Landlord and Tenant Issues',
			],
			'help_code': 'rent_utilities'
		},
		'https://www.pa211.org/get-help/food': {
			'exclude': [
				'Holiday Meals and Baskets',
				'Healthy Eating',
				'Pet Care'
			],
			'help_code': 'food'
		},
		'https://www.pa211.org/get-help/utilities/': {
			'exclude': [],
			'help_code': 'rent_utilities',
		}
	}
	region_code = 'pa'
	delay = 0
	links = []
	next_pages = []
	initial_links_to_follow = []
	search_terms = []
	counter = 0

	def start(self, urls):

		options = Options()
		#options.headless = True

		profile = webdriver.FirefoxProfile()

		self.driver = webdriver.Firefox(firefox_profile=profile, options=options)

		for url, data in urls.items():
			self.driver.get(url)

			time.sleep(3)
			try:
				close = self.driver.find_element_by_xpath('/html/body/div[1]/div[3]/div/div/div/div[2]')

				close.click()

				time.sleep(3)
			except Exception as e:
				print('no alert')

			help_category_elements = self.driver.find_elements_by_css_selector('.help-category-title')
			help_categories = [element for element in help_category_elements if element.text not in urls[url]['exclude']]
			for hc in help_categories:
				hc.click()
				time.sleep(1)
				link_list_element = self.driver.find_element_by_xpath(f'//*[@class="{hc.get_attribute("class")}"]/following-sibling::div')
				link_list_element_list = link_list_element.find_elements_by_tag_name('a')
				for link_in_list in link_list_element_list:
					self.links.append({
						'href': link_in_list.get_attribute('href'),
						'helper_type': urls[url]['help_code']
					})


		for link in self.links:
			self.get_data(link['href'], link['helper_type'])

		self.driver.quit()

	def get_data(self, link, helper_type):


		self.driver.get(link)

		helpers = self.driver.find_elements_by_css_selector('.search-result-item')
		
		for helper in helpers:
			try:	
				title = helper.find_element_by_css_selector(".search-result-item-name").text
				description = helper.find_element_by_css_selector(".search-result-item-description").text
				address = helper.find_element_by_css_selector(".search-result-item-address")
				hours_of_operation = helper.find_element_by_css_selector('.search-result-item-hours').text
				
			except Exception as e:
				print(e)
				return
			try:
				phone = helper.find_element_by_css_selector(
					'.search-result-item-phone').find_element_by_tag_name('a').get_attribute('href').split('tel:')[-1]
			except Exception as e:
				phone = None

			try:
				email = helper.find_element_by_css_selector(
					'search-result-item-email').find_element_by_tag_name('a').get_attribute('href').split('mailto:')[-1]

			except Exception as e:
				email = None

			try:
				eligibility = helper.find_element_by_css_selector('search-result-item-eligibility').text
				description = description + "\n\n" + eligibility
			except Exception as e:
				eligibility = None

			no_website = False
			has_image = False
			try:
				website = helper.find_element_by_css_selector(
					'.search-result-item-name').find_element_by_tag_name('a').get_attribute('href')
			except Exception as e:
				print('could not get website')
				no_website = True
				website = None
				# get thumbnail from website

			if not no_website:
				try:
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
				
			loc_seach_str = re.sub('[^a-zA-Z0-9]', '', address.get_attribute('innerHTML').split('<br>')[-1].split(' ')[0])
			location = search_city(loc_seach_str, self.region_code)

			try:

				if title != '':
					w = WikiEntry.objects.create(
						title=title,
						description=description,
						address=address.text,
						hours_of_operation=hours_of_operation,
						website=website,
						helper_type=helper_type,
						location=location,
						slug=slugify(title)[:50],
						phone_number=phone,
						is_verified=True,
						email=email,
					)

					print(f'added {title}')

					if has_image:
						w.thumbnail.save(f"{slugify(title)}-thumbnail.{img_filetype}", img_temp)
			except Exception as e:
				print(e)

	def handle(self, *args, **kwargs):
		self.start(self.urls)
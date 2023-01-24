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
	help = 'Extract data from 211texas.org'
	first_url = 'https://www.211texas.org'
	delay = 0
	links = []
	next_pages = []
	initial_links_to_follow = []
	search_terms = []
	counter = 0
	classes = {
		#'Housing Expense:Rent Payment' : 'rent_utilities',
		#'Housing Expense:Mortgage Payment' : 'rent_utilities',
		#'Emergency Shelter:ALL': 'rent_utilities',
		'Emergency Food:ALL': 'food',
		'Personal Expenses:ALL': 'other',
		#'Inpatient/Residential Facilities:ALL': 'mental_health_rehab',
	}

	def construct_search_link_base(self, search_term):

		url = f"https://na1.icarol.info/AdvancedSearch.aspx?org=72605&Count=5&NameOnly=True&pst=Coverage&sort=Proximity&TaxExact=False&Country=United+States&StateProvince=TX&County=-1&City=-1&PostalCode=&Search={search_term}"
		return url

	def start(self, initial_url):

		options = Options()
		#options.headless = True

		profile = webdriver.FirefoxProfile()

		self.driver = webdriver.Firefox(firefox_profile=profile, options=options)

		self.driver.get(initial_url)

		for _class, help_code in self.classes.items():
			_class_split = _class.split(':')
			link_category = _class_split[0]
			link_sub_category = _class_split[1]
			link_group = self.driver.find_element_by_link_text(
				link_category
			)

			link_group.click()

			link_group_parent_parent_parent = link_group.find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..')

			if link_sub_category == 'ALL':

				self.search_terms.extend(
					[{'href': link.text, 'helper_type': help_code} for link in link_group_parent_parent_parent.find_elements_by_tag_name('li')])

			else:
				self.search_terms.append({
					'href': link_group.find_element_by_xpath(f"//a[@title='{link_sub_category}']").text,
					'helper_type': help_code
				})


		for search_term in self.search_terms:
			self.follow_link(
				self.construct_search_link_base(search_term['href']),
				search_term['helper_type'])

		for link in self.links:
			self.get_data(link['href'], link['helper_type'])

		self.driver.quit()

	def follow_link(self, link, helper_type):

		self.driver.get(link)

		self.get_data_links(helper_type)
		

	def get_data_links(self, helper_type):
		
		link_elements = [link_base.find_element_by_tag_name('a') for link_base in self.driver.find_elements_by_css_selector('.DetailsHeaderBackground')]

		for link in link_elements:
			self.links.append({
				'href': "https:" + link.get_attribute('onclick').split('window.open("')[-1].split('")')[0], 
				'helper_type': helper_type
			})


		page_info = self.driver.find_element_by_css_selector('.PagerInfoCell').text
		current_page_num = int(self.driver.find_element_by_css_selector('.PagerCurrentPageCell').text)
		print(current_page_num)
		num_pages = int(page_info.split('of ')[-1])

		if current_page_num < num_pages:
			try: 
				next_page_element = self.driver.find_element_by_xpath('//*[@class="PagerCurrentPageCell"]/following-sibling::td')
				next_page_link = next_page_element.find_element_by_tag_name('a')
				next_page_link.click()
				self.get_data_links(helper_type)
			except Exception as e:
				print(e)
				return

	def get_data(self, link, helper_type):


		self.driver.get(link)

		time.sleep(10)

		try:
			self.driver.switch_to.alert.accept()
		except Exception as e:
			print('no alert')
		
		

		self.driver.switch_to.frame(self.driver.find_element_by_css_selector("iframe#find_services_frame"))

		
		try:	
			title = self.driver.find_element_by_css_selector("#hlLinkToParentAgency").text.split('Agency: ')[-1]
			description = self.driver.find_element_by_css_selector("#lblAgencyDescription").text
			address = self.driver.find_element_by_css_selector("#lblAgencyPhysicalAddress")
			hours_of_operation = self.driver.find_element_by_css_selector('#lblAgencyHours').text
		except Exception as e:
			print(e)
			return
		try:
			phone = self.driver.find_element_by_xpath('/html/body/form/div[4]/div[1]/div[3]/table/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[2]/td[1]').text
		except Exception as e:
			phone = None

		no_website = False
		has_image = False
		try:
			website = self.driver.find_element_by_css_selector('#hlAgencyWebsite').get_attribute('href')
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
			
		loc_search_str = re.sub('[^a-zA-Z0-9]', '', address.get_attribute('innerHTML').split('<br>')[-1].split(' ')[0])
		location = search_city(loc_search_str, 'tx')

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
				)

				if has_image:
					w.thumbnail.save(f"{slugify(title)}-thumbnail.{img_filetype}", img_temp)
		except Exception as e:
			print(e)

	def handle(self, *args, **kwargs):
		self.start(self.first_url)
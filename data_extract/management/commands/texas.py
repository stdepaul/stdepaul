from django.core.management.base import BaseCommand

from bs4 import BeautifulSoup

class Command(BaseCommand):
	help = 'Extract data from state 211texas.org'
	first_url = '211texas.org'
	classes = {
		'Housing Expense:Rent Payment' : 'rent_utilities',
		'Housing Expense:Mortgage Payment' : 'rent_utilities',
		'Emergency Shelter:ALL': 'rent_utilities',

	}
	def crawl(initial_url):

	    crawled, to_crawl = [], []
	    to_crawl.append(initial_url)

	    while to_crawl:
	        current_url = to_crawl.pop(0)
	        r = requests.get(current_url)
	        crawled.append(current_url)
	        soup = BeautifulSoup(r.content, 'lxml')



	def handle(self, *args, **kwargs):
		self.crawl(self.first_url)
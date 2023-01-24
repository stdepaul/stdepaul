from wiki.models import WikiEntry
from django.core.management.base import BaseCommand

import http.client, urllib.parse
import os
import json

"""
edit wiki/models.py when done debugging
"""

class Command(BaseCommand):

	help = 'Geocode existing wiki entries'

	def handle(self, *args, **kwargs):
		for w in WikiEntry.objects.filter(location__icontains='co-us'):
			#if not w.latitude and not w.longitude:
			conn = http.client.HTTPConnection('api.positionstack.com')

			try:
				params = urllib.parse.urlencode({
				    'access_key': os.environ.get('STDEPAUL_POSITIONSTACK_ACCESS_KEY'),
				    'query': w.address,
				    'limit': 1,
				})
			except Exception as e:
				print(e)
				continue


			conn.request('GET', '/v1/forward?{}'.format(params))

			res = conn.getresponse()
			data = res.read()
			try:
				longitude = str(json.loads(data.decode('utf-8'))['data'][0]['longitude'])
				latitude = str(json.loads(data.decode('utf-8'))['data'][0]['latitude'])
			except Exception as e:
				print(e)
				continue
			
			w.latitude = latitude
			w.longitude = longitude

			w.save()
			print(f'saved lat/long for {w.title}')
import json
from django.shortcuts import render
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.response import Response
from django.contrib.auth.models import User

from django.core import serializers
from django.template.defaultfilters import slugify

from datetime import datetime, timezone

import subprocess
import os 

from allcities import cities

from wiki.models import WikiEntry
from root_app.models import Helper

import http.client, urllib.parse
import os
import json


@api_view(['GET'])
@permission_classes((AllowAny,))
@ensure_csrf_cookie
def get_location_slug(request):
	loc_query = request.GET.get('term')
	results = cities.filter(name=loc_query)
	results = sorted(results, key=lambda d: d.population, reverse=True)
	results = [f"{city.asciiname.replace(' ', '').lower()}-{city.admin1_code.lower()}-{city.country_code.lower()}" for city in results]
	return Response(results)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
@ensure_csrf_cookie
def get_geoposition(request):
	# only make api request to positionstack if model instance has no coords
	_type = request.GET.get('type')
	pk = request.GET.get('pk')

	if _type == 'helper':
		w = Helper.objects.get(pk=pk)
	elif _type == 'wiki_entry':
		w = WikiEntry.objects.get(pk=pk)
	else:
		return Response('error: invalid type. Must be helper or wiki_entry')

	if not w.latitude and not w.longitude:
		conn = http.client.HTTPConnection('api.positionstack.com')

		try:
			params = urllib.parse.urlencode({
			    'access_key': os.environ.get('STDEPAUL_POSITIONSTACK_ACCESS_KEY'),
			    'query': w.address,
			    'limit': 1,
			})
		except Exception as e:
			print(e)
			return Response('error: invalid params')

		conn.request('GET', '/v1/forward?{}'.format(params))

		res = conn.getresponse()
		data = res.read()

		try:
			longitude = str(json.loads(data.decode('utf-8'))['data'][0]['longitude'])
			latitude = str(json.loads(data.decode('utf-8'))['data'][0]['latitude'])
		except Exception as e:
			print(e)
			return Response(e)
		
		w.latitude = latitude
		w.longitude = longitude

		w.save()

		return Response('success')
	else:
		return Response('error: this already contains lat/lng coords')
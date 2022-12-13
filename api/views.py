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


@api_view(['GET'])
@permission_classes((IsAuthenticated, AllowAny))
@ensure_csrf_cookie
def get_location_slug(request):
	loc_query = request.GET.get('term')
	results = cities.filter(name=loc_query)
	results = [f"{city.country_code.lower()}-{city.admin1_code.lower()}-{city.asciiname.replace(' ', '').lower()}" for city in results]
	return Response(results)
from django.contrib import admin
from django.urls import path, include

from .views import get_location_slug
from .views import get_geoposition

urlpatterns = [
    path('get_location_slug/', get_location_slug, name='get_location_slug'),
    path('get_geoposition/', get_geoposition, name='get_geoposition'),
]

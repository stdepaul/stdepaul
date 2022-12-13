from django.contrib import admin
from django.urls import path, include

from .views import get_location_slug

urlpatterns = [
    path('get_location_slug/', get_location_slug, name='get_location_slug'),
]

from django.contrib import admin

from .models import WikiEntry

@admin.register(WikiEntry)
class WikiEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'location')

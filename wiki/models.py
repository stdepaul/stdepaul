from django.db import models
from root_app.models import HELPER_TYPES
from martor.models import MartorField
from django.template.defaultfilters import slugify

from django.contrib.auth.models import User

from django.conf import settings

from natural_keys import NaturalKeyModel



# __WIKI_LOCATION_HOME__ is the homepage wiki for a given location

RESERVED_TITLES = (
	'__WIKI_LOCATION_HOME__',
)


class WikiEntry(NaturalKeyModel):
	title = models.CharField(max_length=255, default="Untitled")
	helper_type = models.CharField(max_length=255, blank=True, null=True, choices=HELPER_TYPES)
	description = MartorField(blank=True, null=True)

	thumbnail = models.ImageField(
		upload_to="wiki_entry_thumbnails", blank=True, null=True)
	cover_photo = models.ImageField(
		upload_to="wiki_entry_cover_photos", blank=True, null=True)

	hours_of_operation = models.TextField(blank=True, null=True)
	moderators = models.ManyToManyField(User, related_name="wiki_moderated_by")

	location = models.CharField(max_length=255, blank=True, null=True)
	address = models.CharField(max_length=255, blank=True, null=True)
	phone_number = models.CharField(max_length=255, blank=True, null=True)

	slug = models.SlugField(max_length=50, blank=True, null=True)

	created_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	website = models.URLField(blank=True, null=True)
	email = models.CharField(max_length=255, blank=True, null=True)

	is_verified = models.BooleanField(default=False)

	class Meta:

		unique_together = [['title', 'address', 'description']]

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)[:50]

		return super(WikiEntry, self).save(*args, **kwargs)

	def get_object_type(self):
		return 'Wiki Entry'

	def __str__(self):
		return self.title

	def get_thumbnail_url(self):
		return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.us-east-2.amazonaws.com/{self.thumbnail}"

	def get_cover_photo_url(self):
		return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.us-east-2.amazonaws.com/{self.cover_photo}"
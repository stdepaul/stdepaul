from django.db import models
from root_app.models import HELPER_TYPES
from martor.models import MartorField

from django.contrib.auth.models import User

class WikiEntry(models.Model):
	title = models.CharField(max_length=255)
	helper_type = models.CharField(max_length=255, blank=True, null=True, choices=HELPER_TYPES)
	body = MartorField(blank=True, null=True)

	thumbnail = models.ImageField(
		upload_to="helper_thumbnails", blank=True, null=True)
	cover_photo = models.ImageField(
		upload_to="helper_cover_photos", blank=True, null=True)

	hours_of_operation = models.TextField()
	moderators = models.ManyToManyField(User, related_name="wiki_moderated_by")

	location = models.CharField(max_length=255, blank=True, null=True)
	address = models.CharField(max_length=255, blank=True, null=True)
	phone_number = models.CharField(max_length=255, blank=True, null=True)

	slug = models.SlugField(max_length=50, blank=True, null=True)

	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)[:50]

		return super(Organization, self).save(*args, **kwargs)

	def __str__(self):
		return self.name
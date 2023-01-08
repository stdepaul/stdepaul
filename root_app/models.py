from django.db import models

from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

from django.urls import reverse

from django.contrib.contenttypes.fields import GenericRelation
from vote.models import VoteModel
from datetime import datetime, timezone, timedelta
from PIL import Image
from django.core.files.storage import default_storage as storage
from django.core.files.base import ContentFile, File
from django.urls import reverse, reverse_lazy
from itertools import chain
from martor.models import MartorField

import http.client, urllib.parse
import os
import json

from django.conf import settings

HELPER_TYPES = (
	('food', 'Food Assistance'),
	('rent_utilities', 'Housing / Rent Assistance'),
	('entry_level_job', 'Entry-Level Job Employer'),
	('develop_skills', 'Job Skills Educator'),
	('mental_health_rehab', 'Mental Health or Rehab Services'),
	('scholarships', 'Scholarship Offerer'),
	('other', 'Other'),
)

class Helper(models.Model):
	
	title = models.CharField(max_length=255, default="Untitled")
	description = MartorField(blank=True, null=True)
	thumbnail = models.ImageField(
		upload_to="helper_thumbnails", blank=True, null=True)
	cover_photo = models.ImageField(
		upload_to="helper_cover_photos", blank=True, null=True)
	hours_of_operation = models.TextField(blank=True, null=True)
	moderators = models.ManyToManyField(User, related_name="moderated_by")

	location = models.CharField(max_length=255, null=True, blank=True)

	address = models.CharField(max_length=255, blank=True, null=True)
	phone_number = models.CharField(max_length=255, blank=True, null=True)

	slug = models.SlugField(max_length=50, blank=True, null=True)

	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	helper_type = models.CharField(max_length=255, blank=True, null=True, choices=HELPER_TYPES)

	website = models.URLField(blank=True, null=True)

	email = models.CharField(max_length=255, blank=True, null=True)

	verification_document_1 = models.ImageField(
		upload_to="helper_verification_document_1_folder", blank=True, null=True)

	verification_document_2 = models.ImageField(
		upload_to="helper_verification_document_2_folder", blank=True, null=True)

	is_verified = models.BooleanField(default=False)

	latitude = models.CharField(max_length=255, blank=True, null=True)
	longitude = models.CharField(max_length=255, blank=True, null=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)[:50]

		if not self.latitude and not self.longitude:
			conn = http.client.HTTPConnection('api.positionstack.com')

			try:
				params = urllib.parse.urlencode({
				    'access_key': os.environ.get('STDEPAUL_POSITIONSTACK_ACCESS_KEY'),
				    'query': self.address,
				    'limit': 1,
				})
			except Exception as e:
				print(e)
				return

			conn.request('GET', '/v1/forward?{}'.format(params))

			res = conn.getresponse()
			data = res.read()

			try:
				longitude = str(data.decode('utf-8')['data'][0]['longitude'])
				latitude = str(data.decode('utf-8')['data'][0]['latitude'])
			except Exception as e:
				print(e)
				return
			
			self.latitude = latitude
			self.longitude = longitude

		return super(Helper, self).save(*args, **kwargs)

	def __str__(self):
		return self.title

	def get_object_type(self):
		return 'Helper'

	def get_url(self):
		return reverse("helper_detail", kwargs={
			'location': str(self.location),
			'pk': str(self.id),
			'slug': str(self.slug)})

	def get_thumbnail_url(self):
		if self.thumbnail:
			return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.us-east-2.amazonaws.com/{self.thumbnail}"
		else:
			return "/static/img/stdepaulsqblue.png"


	def get_cover_photo_url(self):
		return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.us-east-2.amazonaws.com/{self.cover_photo}"

RULES = (
	('ISILL', 'Is illegal'),
	('ISAIM', 'Promotes AI/ML'),
	('ISSPA', 'Is spam'),
	('ISHAT', 'Is hate speech'),
	('ISSCA', 'Is a scam'),
	('INAPP', 'Is Inappropriate'),
	('OTHER', 'Other')
)

POST_TYPES = (
	('helpers_indv', 'helpers'),
	('helpees', 'helpees'),
)

class Post(VoteModel, models.Model):

	title = models.CharField(max_length=255, default="Untitled")
	description = MartorField(blank=True, null=True)
	slug = models.SlugField(blank=True, null=True)
	image = models.ImageField(upload_to="post_images/")

	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	post_type = models.CharField(max_length=255, choices=POST_TYPES, blank=True, null=True)
	help_type = models.CharField(max_length=255, choices=HELPER_TYPES, blank=True, null=True)

	location = models.CharField(max_length=255, blank=True, null=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.title)[:50]

		"""
		image = Image.open(self.image)
		s3_image = storage.open(self.image.name, "wb")
		picture_format = 'png'
		image.save(s3_image, picture_format, optimize=True, quality=95)
		s3_image.close() 

		self.image.save(self.image.name.split('post_images/')[1], File(self.image), save=False)
		"""

		return super(Post, self).save(*args, **kwargs)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse("post_detail", kwargs={
			'location': str(self.location),
			'pk': str(self.id),
			'slug': str(self.slug)})

	def get_time_sensitive_vote_score(self):
		p = self.vote_score
		t = (datetime.now(timezone.utc) - self.created_at).total_seconds()
		g = 1.8
		return p / (t + 2) ** g

	def get_url(self):
		return reverse("post_detail", kwargs={
			'location': str(self.location),
			'pk': str(self.id),
			'slug': str(self.slug)})

	def get_object_type(self):
		return f'Post ({self.get_post_type_display()})'

	def get_thumbnail_url(self):
		if self.thumbnail:
			return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.us-east-2.amazonaws.com/{self.thumbnail}"
		else:
			return "/static/img/stdepaulsqblue.png"

	def get_cover_photo_url(self):
		return f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.us-east-2.amazonaws.com/{self.cover_photo}"

class PostReport(models.Model):
	post = models.ForeignKey('Post', on_delete=models.CASCADE)
	description = models.CharField(max_length=10000)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	rule_broken = models.CharField(max_length=255, choices=RULES)

class Comment(VoteModel, models.Model):
	
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	text = MartorField(blank=True, null=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "%s..." % (self.text[:25])

	def get_time_sensitive_vote_score(self):
		p = self.vote_score
		t = (datetime.now(timezone.utc) - self.datetime).total_seconds()
		g = 1.8
		return p / (t + 2) ** g

	def get_absolute_url(self):
	   
		return reverse('post_detail', kwargs={
			'pk': self.post.pk,
			'slug': self.post.slug,
		})

class CommentReport(models.Model):
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
	description = models.CharField(max_length=10000)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	rule_broken = models.CharField(max_length=255, choices=RULES)

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	
	bio = MartorField(blank=True, null=True)
	name = models.CharField(max_length=255, blank=True, null=True)
	thumbnail = models.ImageField(
		upload_to="user_thumbnails", blank=True, null=True)
	cover_photo = models.ImageField(
		upload_to="user_cover_photos", blank=True, null=True)

	location = models.CharField(max_length=255, blank=True, null=True)

	slug = models.SlugField(max_length=50, blank=True, null=True)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.user.username)[:50]

		return super(UserProfile, self).save(*args, **kwargs)

	def __str__(self):
		return self.user.username

	@property
	def is_helper(self):
		return Helper.objects.filter(created_by=self.user).exists()

	def get_absolute_url(self):
	   
		return reverse('profile', kwargs={
			'user': self.slug,
		})
	

def create_profile(sender, instance, created, **kwargs):
	if created:
		_u = User.objects.get(username=instance)
		profile, created = UserProfile.objects.get_or_create(
			user=instance)

post_save.connect(create_profile, sender=User)	
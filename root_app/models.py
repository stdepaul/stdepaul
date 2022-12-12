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

HELPER_TYPES = (
	('FDBNK', 'Food Assistance'),
	('REUAS', 'Rent / Utilities Assistance'),
	('ELEMP', 'Entry-Level Job Employer'),
	('JOSKT', 'Job Skills Educator'),
	('MHSER', 'Mental Health Services Organization or Individual'),
	('DAREH', 'Drug / Alcohol Rehab Services Organization'),
	('SCHOL', 'Scholarship Offerer'),
	('OTHER', 'Other'),
)

class Helper(models.Model):
	
	name = models.CharField(max_length=255, blank=True, null=True)
	description = MartorField(blank=True, null=True)
	thumbnail = models.ImageField(
		upload_to="helper_thumbnails", blank=True, null=True)
	cover_photo = models.ImageField(
		upload_to="helper_cover_photos", blank=True, null=True)
	hours_of_operation = MartorField(blank=True, null=True)
	moderators = models.ManyToManyField(User, related_name="moderated_by")

	location = models.CharField(max_length=255, null=True, blank=True)

	address = models.CharField(max_length=255, blank=True, null=True)
	phone_number = models.CharField(max_length=255, blank=True, null=True)

	slug = models.SlugField(max_length=50, blank=True, null=True)

	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	helper_type = models.CharField(max_length=255, blank=True, null=True, choices=HELPER_TYPES)

	verification_document_1 = models.ImageField(
		upload_to="helper_verification_document_1_folder", blank=True, null=True)

	verification_document_2 = models.ImageField(
		upload_to="helper_verification_document_2_folder", blank=True, null=True)

	is_verified = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.name)[:50]

		return super(Helper, self).save(*args, **kwargs)

	def __str__(self):
		return self.name

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
	('IWTH', 'I want to help'),
	('INH', 'I need help'),
)

class Post(VoteModel, models.Model):

	title = models.CharField(max_length=255, blank=True, null=True)
	body = MartorField(blank=True, null=True)
	slug = models.SlugField(blank=True, null=True)
	image = models.ImageField(upload_to="post_images/")

	created_by = models.ForeignKey(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	help_type = models.CharField(max_length=255, choices=POST_TYPES, blank=True, null=True)

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
			'pk': str(self.id),
			'slug': str(self.slug)})

	def get_time_sensitive_vote_score(self):
		p = self.vote_score
		t = (datetime.now(timezone.utc) - self.created_at).total_seconds()
		g = 1.8
		return p / (t + 2) ** g

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

	is_helper = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		if not self.slug:
			self.slug = slugify(self.user.username)[:50]

		return super(UserProfile, self).save(*args, **kwargs)

	def __str__(self):
		return self.user.username

def create_profile(sender, instance, created, **kwargs):
	if created:
		_u = User.objects.get(username=instance)
		profile, created = UserProfile.objects.get_or_create(
			user=instance)

post_save.connect(create_profile, sender=User)	
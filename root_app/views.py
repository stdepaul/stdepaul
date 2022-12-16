from django.shortcuts import render

import os 
import re
import urllib
import inspect
import random
import string
import markdown

from itertools import chain

from django.shortcuts import render
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.search import SearchRank
from django.contrib.postgres.search import SearchQuery
from django_messages.models import Message

from datetime import datetime, timezone

from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from django.shortcuts import redirect

from django.conf import settings

from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView

from .forms import UserProfileForm
from .forms import PostForm
from .forms import CommentForm
from .forms import HelperForm

from django.core.paginator import Paginator

from .models import UserProfile
from .models import Post
from .models import Comment
from .models import Helper

from wiki.models import WikiEntry

from allcities import cities

import pandas as pd 

def home(request):
	context = {}
	template_name = 'home.html'
	return render(request, template_name, context)

def about(request):
	context = {

	}
	template_name = 'root_app/about.html'
	return render(request, template_name, context)

def terms(request):
	context = {

	}
	template_name = 'root_app/terms.html'
	return render(request, template_name, context)

def privacy(request):
	context = {

	}
	template_name = 'root_app/privacy.html'
	return render(request, template_name, context)

def rules(request):
	context = {

	}
	template_name = 'root_app/rules.html'
	return render(request, template_name, context)

def my_organizations(request):
	organizations = Helper.objects.filter(created_by=request.user)
	context = {
		'organizations': organizations
	}
	template_name = 'root_app/my_organizations.html'
	return render(request, template_name, context)

def become_a_moderator(request):
	context = {
	}
	template_name = 'root_app/become_a_moderator.html'
	return render(request, template_name, context)

def api_home(request):
	context = {
	}
	template_name = 'root_app/api_home.html'
	return render(request, template_name, context)

def search_city(parsed_location, region=None):

	if parsed_location != '':
		if '-' not in parsed_location and parsed_location != 'global':
			parsed_location = re.sub('[^a-zA-Z0-9]', ' ', parsed_location)
			all_countries = pd.read_csv(os.path.join(settings.BASE_DIR, 'static/assets/countrycodes.csv'))
			if parsed_location not in [str(country_code).lower() for country_code in all_countries['alpha-2']]:

				results = cities.filter(name=parsed_location)
				# get city result with highest population

				if len(list(results)) > 0:
					city = list(results)[0]
					for result in results:
						if region == result.admin1_code.lower():
							city = result 
							break
						elif result.population > city.population:
							city = result

					parsed_location = f"{city.asciiname.replace(' ', '').lower()}-{city.admin1_code.lower()}-{city.country_code.lower()}"
				else:
					parsed_location = 'global'

			else:
				parsed_location = parsed_location

		elif '-' in parsed_location:
			parsed_location_split_len = len(parsed_location.split('-'))
			if parsed_location_split_len == 1:
				parsed_location = re.sub('[^a-zA-Z0-9]', ' ', parsed_location)
				results = cities.filter(name=parsed_location)
				if len(list(results)) > 0:
					city = list(results)[0]
					parsed_location = f"{city.asciiname.replace(' ', '').lower()}-{city.admin1_code.lower()}-{city.country_code.lower()}"
				else:
					parsed_location = 'global'
			elif parsed_location_split_len == 2:
				parsed_location = re.sub('[^a-zA-Z0-9-]', '', parsed_location)
				all_countries = pd.read_csv(os.path.join(settings.BASE_DIR, 'static/assets/countrycodes.csv'))
				if parsed_location.split('-')[-1] not in [str(country_code).lower() for country_code in all_countries['alpha-2']]:
					results = cities.filter(name=parsed_location.split('-')[0])
					for result in results:
						if result.admin1_code.lower() == parsed_location.split('-')[-1] and result.asciiname.replace(' ','').lower() == parsed_location.split('-')[0]:
							city = result
							parsed_location = f"{city.asciiname.replace(' ', '').lower()}-{city.admin1_code.lower()}-{city.country_code.lower()}"
							break
			else:
				parsed_location = re.sub('[^a-zA-Z0-9-]', '', parsed_location)
	else:
		parsed_location = 'global'

	return parsed_location

def posts(request, location):
	
	q = request.GET.get('q', '')
	search_types = request.GET.getlist('search_types[]', [])
	help_types = request.GET.getlist('help_types[]', [])
	parsed_location = request.GET.get('location', location).lower()
	query = SearchQuery(q)

	parsed_location = search_city(parsed_location)
				
	posts = []
	helpers = []
	wiki_entries = []

	if len(search_types) == 0:
		search_types = ['helpees', 'helpers_indv', 'helpers_org', 'wiki_entries']

	def filter_location(item_list, input_location):
		location_split_len = len(input_location.split('-'))
		if location_split_len > 0 and location_split_len < 3:
			item_list = item_list.filter(location__endswith=input_location)
		elif location_split_len == 3:
			item_list = item_list.filter(location=input_location)
		else:
			item_list = item_list.filter(location='global')
		return item_list

	if 'helpees' in search_types or 'helpers_indv' in search_types:
		posts = Post.objects.all()
		if search_types:
			posts = posts.filter(post_type__in=search_types)
		if help_types:
			posts = posts.filter(help_type__in=help_types)
		if q:
			posts = posts.annotate(search=SearchVector(
				'title', 'description', 'created_by', 'location')).filter(search=q)
		if location != 'global':
			posts = filter_location(posts, parsed_location)
			

		posts = posts.order_by('created_at')

	if 'helpers_org' in search_types:
		helpers = Helper.objects.all()
		if help_types:
			helpers = helpers.filter(helper_type__in=help_types)
		if q:
			helpers = helpers.annotate(search=SearchVector(
				'title', 'description', 'moderators', 'created_by', 'location', 'address')).filter(search=q)
		if location != 'global':
			helpers = filter_location(helpers, parsed_location)
		helpers = helpers.filter(is_verified=True).order_by('created_at')

	if 'wiki_entries' in search_types:
		wiki_entries = WikiEntry.objects.all()

		if help_types:
			wiki_entries = wiki_entries.filter(helper_type__in=help_types)
		if q:
			wiki_entries = wiki_entries.annotate(search=SearchVector(
				'title', 'description', 'moderators', 'created_by', 'location', 'address')).filter(search=q)
		if location != 'global':
			wiki_entries = filter_location(wiki_entries, parsed_location)

		wiki_entries = wiki_entries.filter(is_verified=True).order_by('created_at')

	all_items = list(chain(wiki_entries, posts, helpers))

	paginator = Paginator(all_items, 30)
	page = request.GET.get('page')
	results = paginator.get_page(page)

	context = {
		'posts': results,
		'num_results': len(all_items),
		'location': location,
		'q': q,
	}
	template = 'root_app/posts.html'
	if location != parsed_location:
		return redirect(reverse('posts_home', kwargs={'location': parsed_location}) + '?' + request.GET.urlencode(), context)
	else:
		return render(request, template, context)

def profile(request, user):
	
	user_object = User.objects.get(userprofile__slug=user)

	posts = Post.objects.filter(created_by=user_object)

	paginator = Paginator(posts, 10)
	page = request.GET.get('page')
	results = paginator.get_page(page)

	context = {
		'profile':user_object,
		'is_social': True,
		'posts': results
	}
	template = 'root_app/profile.html'
	return render(request, template, context)

def inbox(request):

	inbox = Message.objects.inbox_for(request.user)
	outbox = Message.objects.outbox_for(request.user)

	messages_users_inbox = []
	messages_users_outbox = []
	message_list_inbox = []
	message_list_outbox = []

	for message in inbox:
		if message.sender not in messages_users_inbox:
			messages_users_inbox.append(message.sender)

	# we don't want duplicate messages_users
	for message in outbox:
		if message.recipient not in messages_users_outbox and message.recipient not in messages_users_inbox:
			messages_users_outbox.append(message.recipient)

	# get only last message from each user in sorted messages
	for u in messages_users_inbox:
		latest_message = Message.objects.filter(
			sender=u, recipient=request.user).order_by('-sent_at')[0]
		message_list_inbox.append(latest_message)

	for u in messages_users_outbox:
		latest_message = Message.objects.filter(sender=request.user,
												recipient=u).order_by('-sent_at')[0]
		message_list_outbox.append(latest_message)

	# make dummy values for list with less values for zip
	# zip shortens zip object to the len() of the smaller list by default
	# so this is a workaround

	if len(message_list_outbox) > len(message_list_inbox):
		for i in range(len(message_list_outbox) - len(message_list_inbox)):
			message_list_inbox.append(None)

	if len(message_list_inbox) > len(message_list_outbox):
		for i in range(len(message_list_inbox) - len(message_list_outbox)):
			message_list_outbox.append(None)

	# we return a datetime object if None so
	# the sorted function won't freak out

	message_list = sorted(zip(
		message_list_inbox, message_list_outbox), 
	key=lambda instance: datetime.now(timezone.utc) if instance[1] == None else instance[1].sent_at)

	context = {
		'message_list': message_list,
	}

	return render(request, 'django_messages/inbox.html', context)


class CommentCreateView(CreateView):
	model = Comment
	form_class = CommentForm
	template_name = 'engine/comment_create.html'

	def form_valid(self, form):
		f = form.save(commit=False)
		f.created_by = self.request.user
		f.save()

		return super(CommentCreateView, self).form_valid(form)

	def get_context_data(self, **kwargs):
		context = super(CommentCreateView, self).get_context_data(**kwargs)
		context['is_social'] = True
		return context


class CommentDeleteView(DeleteView):
	model = Comment
	success_url = reverse_lazy('home')
	template_name = 'engine/comment_confirm_delete.html'

	def get_success_url(self, **kwargs):
		return reverse("post_detail", kwargs={
			'pk': str(self.object.post.pk),
			'slug': str(self.object.slug)})

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return self.object.created_by == request.user
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			return redirect(reverse('profile', kwargs={'slug': request.user}))
		return super(CommentDeleteView, self).dispatch(
			request, *args, **kwargs)


class PostCreateView(CreateView):
	model = Post
	form_class = PostForm
	template_name = 'root_app/post_create.html'

	def get_success_url(self, **kwargs):
		return reverse("post_detail", kwargs={
			'location': str(self.object.location),
			'pk': str(self.object.pk),
			'slug': str(self.object.slug)})

	def get_context_data(self, **kwargs):
		context = super(PostCreateView, self).get_context_data(**kwargs)
		context['location'] = self.kwargs['location']
		return context

	def form_valid(self, form):
		f = form.save(commit=False)
		f.created_by = self.request.user
		f.save()

		return super(PostCreateView, self).form_valid(form)

class PostDetailView(DetailView):
	model = Post
	template_name = 'root_app/post_detail.html'

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['user'] = self.request.user
		return kwargs

	def get_success_url(self):
		return reverse("post_detail", kwargs={
			'pk': str(self.kwargs['pk']),
			'slug': str(self.kwargs['slug'])})

	def get_context_data(self, **kwargs):
		context = super(PostDetailView, self).get_context_data(**kwargs)
		comments = Comment.objects.filter(post=self.kwargs['pk'])
		context['comments'] = comments
		context['comments_num'] = len(comments)
		context['comment_form'] = CommentForm
		return context

class PostUpdateView(UpdateView):
	model = Post
	form_class = PostForm
	template_name = 'root_app/post_update.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return self.object.created_by == request.user
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			return redirect(reverse('post_detail', kwargs={
				'pk': self.object.pk,
				'slug': self.object.slug
			}))
		return super(PostUpdateView, self).dispatch(
			request, *args, **kwargs)


class PostDeleteView(DeleteView):
	model = Post
	success_url = reverse_lazy('home')
	template_name = 'root_app/post_confirm_delete.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return self.object.created_by == request.user
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			return redirect(reverse('post_detail', kwargs={
				'pk': self.object.pk,
				'slug': self.object.slug
			}))
		return super(PostDeleteView, self).dispatch(
			request, *args, **kwargs)


class HelperCreateView(CreateView):
	model = Helper
	form_class = HelperForm
	template_name = 'root_app/helper_create.html'

	def get_success_url(self, **kwargs):
		return reverse("helper_detail", kwargs={
			'location': str(self.object.location),
			'pk': str(self.object.pk),
			'slug': str(self.object.slug)})

	def form_valid(self, form):
		f = form.save(commit=False)
		f.created_by = self.request.user
		f.moderators.add(self.request.user)
		f.save()

		return super(HelperCreateView, self).form_valid(form)

class HelperDetailView(DetailView):
	model = Helper
	template_name = 'root_app/helper_detail.html'

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['user'] = self.request.user
		return kwargs

	def get_context_data(self, **kwargs):
		context = super(HelperDetailView, self).get_context_data(**kwargs)
		return context

class HelperUpdateView(UpdateView):
	model = Helper
	form_class = HelperForm
	template_name = 'root_app/helper_update.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return self.object.created_by == request.user
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			return redirect(reverse('helper_detail', kwargs={
				'location': self.object.location,
				'pk': self.object.pk,
				'slug': self.object.slug
			}))
		return super(HelperUpdateView, self).dispatch(
			request, *args, **kwargs)

	def get_success_url(self, **kwargs):
		return reverse("helper_detail", kwargs={
			'location': str(self.object.location),
			'pk': str(self.object.pk),
			'slug': str(self.object.slug)})

class HelperDeleteView(DeleteView):
	model = Helper
	success_url = reverse_lazy('home')
	template_name = 'root_app/helper_confirm_delete.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return self.object.created_by == request.user
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			return redirect(reverse('helper_detail', kwargs={
				'location': self.object.location,
				'pk': self.object.pk,
				'slug': self.object.slug
			}))
		return super(HelperDeleteView, self).dispatch(
			request, *args, **kwargs)


class ProfileUpdateView(UpdateView):
	model = UserProfile
	form_class = UserProfileForm
	template_name = 'root_app/profile_update.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return self.object.user == request.user
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			return redirect(reverse('profile', kwargs={
				'slug': request.user.userprofile.slug}))
		return super(ProfileUpdateView, self).dispatch(
			request, *args, **kwargs)
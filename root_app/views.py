from django.shortcuts import render
import inspect
import random
import string
import markdown

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

def home(request):
	context = {

	}
	template_name = 'home.html'
	return render(request, template_name, context)

def about(request):
	context = {

	}
	template_name = 'about.html'
	return render(request, template_name, context)

def terms(request):
	context = {

	}
	template_name = 'terms.html'
	return render(request, template_name, context)

def privacy(request):
	context = {

	}
	template_name = 'privacy.html'
	return render(request, template_name, context)

def rules(request):
	context = {

	}
	template_name = 'rules.html'
	return render(request, template_name, context)

def posts(request, location):

	posts = Post.objects.filter(location=location)

	paginator = Paginator(posts, 30)
	page = request.GET.get('page')
	results = paginator.get_page(page)

	context = {
		'posts': results
	}
	template = 'profile.html'
	return render(request, template, context)

def profile(request, user):
	
	user_object = User.objects.get(userprofile__slug=user)

	posts = Post.objects.filter(creator=user_object)

	paginator = Paginator(posts, 10)
	page = request.GET.get('page')
	results = paginator.get_page(page)

	context = {
		'profile': UserProfile.objects.get(slug=user),
		'is_social': True,
		'posts': results
	}
	template = 'profile.html'
	return render(request, template, context)


def search(request):
	q = request.GET.get('q', None)
	search_type = request.GET.get('search_type', None) # I want to help
	query = SearchQuery(q)

	posts = Post.objects.annotate(search=SearchVector('title', 'body', 'created_by')).filter(search=q)
	helpers = Helper.objects.annotate(search=SearchVector('name', 'description', 'moderators', 'created_by')).filter(search=q)
	wiki_entries = WikiEntry.objects.annotate(search=SearchVector('name', 'description', 'moderators', 'created_by')).filter(search=q)

	paginator = Paginator(result_items, 25)
	page = request.GET.get('page')
	results = paginator.get_page(page)

	context = {
		'results': results,
		'q': q,
		'item_type': item_type,
	}
	return render(request,
				  'search.html',
				  context)


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
		f.creator = self.request.user
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
			return self.object.creator == request.user
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			return redirect(reverse('profile', kwargs={'slug': request.user}))
		return super(CommentDeleteView, self).dispatch(
			request, *args, **kwargs)


class PostCreateView(CreateView):
	model = Post
	form_class = PostForm
	template_name = 'engine/post_create.html'

	def get_success_url(self, **kwargs):
		return reverse("post_detail", kwargs={
			'pk': str(self.object.pk),
			'slug': str(self.object.slug)})

	def get_context_data(self, **kwargs):
		context = super(PostCreateView, self).get_context_data(**kwargs)
		context['is_social'] = True
		return context

class PostDetailView(DetailView):
	model = Post
	template_name = 'engine/post_detail.html'

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
		context['markdown_body'] = markdown.markdown(Post.objects.get(pk=self.kwargs['pk']).body)
		context['is_social'] = True
		return context

class PostUpdateView(UpdateView):
	model = Post
	form_class = PostForm
	template_name = 'engine/post_update.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return self.object.creator == request.user
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
	template_name = 'engine/post_confirm_delete.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return self.object.creator == request.user
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
			'pk': str(self.object.pk),
			'slug': str(self.object.slug)})

class HelperDetailView(DetailView):
	model = Helper
	template_name = 'root_app/helper_detail.html'

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['user'] = self.request.user
		return kwargs

	def get_success_url(self):
		return reverse("helper_detail", kwargs={
			'pk': str(self.kwargs['pk']),
			'slug': str(self.kwargs['slug'])})

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
			return self.object.creator == request.user
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			return redirect(reverse('helper_detail', kwargs={
				'pk': self.object.pk,
				'slug': self.object.slug
			}))
		return super(HelperUpdateView, self).dispatch(
			request, *args, **kwargs)

class HelperDeleteView(DeleteView):
	model = Post
	success_url = reverse_lazy('home')
	template_name = 'root_app/helper_confirm_delete.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return self.object.creator == request.user
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			return redirect(reverse('helper_detail', kwargs={
				'pk': self.object.pk,
				'slug': self.object.slug
			}))
		return super(HelperDeleteView, self).dispatch(
			request, *args, **kwargs)


class ProfileUpdateView(UpdateView):
	model = UserProfile
	form_class = UserProfileForm
	template_name = 'engine/profile_update.html'

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
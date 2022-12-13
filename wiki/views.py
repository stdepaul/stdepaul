from django.shortcuts import render
import inspect
import random
import string
import markdown

from django.shortcuts import render
from django.contrib.postgres.search import SearchVector
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



from django.core.paginator import Paginator

from .models import WikiEntry

from .forms import WikiEntryForm

from root_app.models import Comment

from root_app.forms import CommentForm

def wiki_home(request, location):

	if location != 'global':
		location_arr = location.split('-')
		city = location_arr[0]
		state_province = location_arr[1]
		country = location_arr[2]

	context = {

	}

	template_name = 'wiki/home.html'
	return render(request, template_name, context)

class WikiEntryCreateView(CreateView):
	model = WikiEntry
	form_class = WikiEntryForm
	template_name = 'wiki/entry_create.html'

	def get_success_url(self, **kwargs):
		return reverse("wiki_entry_detail", kwargs={
			'location': str(self.object.location),
			'pk': str(self.object.pk),
			'slug': str(self.object.slug)})

	def get_context_data(self, **kwargs):
		context = super(WikiEntryCreateView, self).get_context_data(**kwargs)
		context['location'] = self.kwargs['location']
		return context

	def form_valid(self, form):
		f = form.save(commit=False)
		f.created_by = self.request.user
		f.moderators.add(self.request.user)
		f.save()

		return super(WikiEntryCreateView, self).form_valid(form)

class WikiEntryDetailView(DetailView):
	model = WikiEntry
	template_name = 'wiki/entry_detail.html'

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs['user'] = self.request.user
		return kwargs

	def get_context_data(self, **kwargs):
		context = super(WikiEntryDetailView, self).get_context_data(**kwargs)
		comments = Comment.objects.filter(post=self.kwargs['pk'])
		context['comments'] = comments
		context['comments_num'] = len(comments)
		context['comment_form'] = CommentForm
		return context

class WikiEntryUpdateView(UpdateView):
	model = WikiEntry
	form_class = WikiEntryForm
	template_name = 'wiki/entry_update.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return self.object.created_by == request.user
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			return redirect(reverse('wiki_entry_detail', kwargs={
				'location': self.object.location,
				'pk': self.object.pk,
				'slug': self.object.slug
			}))
		return super(WikiEntryUpdateView, self).dispatch(
			request, *args, **kwargs)

	def get_success_url(self, **kwargs):
		return reverse("wiki_entry_detail", kwargs={
			'location': str(self.object.location),
			'pk': str(self.object.pk),
			'slug': str(self.object.slug)})


class WikiEntryDeleteView(DeleteView):
	model = WikiEntry
	success_url = reverse_lazy('wiki_home')
	template_name = 'wiki/entry_confirm_delete.html'

	def user_passes_test(self, request):
		if request.user.is_authenticated:
			self.object = self.get_object()
			return self.object.created_by == request.user
		return False

	def dispatch(self, request, *args, **kwargs):
		if not self.user_passes_test(request):
			return redirect(reverse('wiki_entry_detail', kwargs={
				'pk': self.object.pk,
				'slug': self.object.slug
			}))
		return super(WikiEntryDeleteView, self).dispatch(
			request, *args, **kwargs)

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

from root_app.models import Post
from root_app.models import Comment
from root_app.models import UserProfile
from root_app.models import Helper

class PostForm(forms.ModelForm):

    # captcha = ReCaptchaField(widget=ReCaptchaV3())

    class Meta:
        model = Post
        exclude = ('slug', 'created_by', 'created_at', 'updated_at', 'vote_score', 'num_vote_up', 'num_vote_down')

class CommentForm(forms.ModelForm):

    # captcha = ReCaptchaField()

    class Meta:
        model = Comment
        exclude = ('created_by', 'post', 'created_at', 'vote_score', 'num_vote_up', 'num_vote_down')

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        exclude = ('slug', 'user')

class HelperForm(forms.ModelForm):

    # captcha = ReCaptchaField(widget=ReCaptchaV3())

    class Meta:
        model = Helper
        exclude = ('slug', 'created_by', 'created_at', 'updated_at', 'is_verified', 'verification_document_1', 'verification_document_2', 'moderators')

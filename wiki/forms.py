from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3

from .models import WikiEntry

class WikiEntryForm(forms.ModelForm):

    # captcha = ReCaptchaField(widget=ReCaptchaV3())

    class Meta:
        model = WikiEntry
        exclude = ('slug', 'created_by', 'created_at', 'updated_at', 'moderators', 'is_verified', 'latitude', 'longitude', 'cover_photo')

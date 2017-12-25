from _socket import herror
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.utils import timezone
from django import forms
from django.forms import EmailField
import datetime
now = timezone.now()


class UserCreationForm(UserCreationForm):
    email = EmailField(label=_("Email address"), required=True,
        help_text=_("Required."))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class createAuction(forms.Form):
    title = forms.CharField(required=True)
    description = forms.CharField(widget=forms.Textarea(), required=False)
    price = forms.DecimalField(required=True)
    deadline = forms.DateTimeField(input_formats=['%d-%m-%Y %H:%M'], help_text="Please use the following format: <em>01-01-2017 23:59</em>")

    def clean(self):
        deadline = self.cleaned_data['deadline']
        if deadline < (datetime.datetime.now() + datetime.timedelta(days=3)):
            raise forms.ValidationError("The date cannot be in the past!")

class bidAuction(forms.Form):
    price = forms.DecimalField(required=True)


class confAuction(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)
    a_title = forms.CharField(widget=forms.HiddenInput())
    a_description = forms.CharField(widget=forms.HiddenInput())
    a_price = forms.DecimalField(widget=forms.HiddenInput())
    a_time = forms.DateTimeField(widget=forms.HiddenInput())

class confBan(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)
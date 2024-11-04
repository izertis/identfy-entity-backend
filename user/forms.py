from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class MyUserForm(UserCreationForm):
    email = forms.CharField(
        label=_("Email"),
        max_length=100,
        required=True,
        widget=forms.EmailInput,
        help_text=_("Required. 100 characters or fewer. Email format only."),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

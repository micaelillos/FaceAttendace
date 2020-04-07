from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)
    school_code = forms.CharField(max_length=8)
    teacher_id = forms.CharField(max_length=200, required=False, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'school_code', 'password1', 'password2',)
        help_texts = {
            'username': None,
            'email': None,
            'Password': None,
            'Password confirmation': None,
        }
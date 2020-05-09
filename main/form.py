from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from main.models import *


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)
    school_code = forms.CharField(max_length=10)
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


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

    username = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username', 'id': 'hello'}), label='')
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'hi',
        }
    ), label='')


class NewStudentForm(forms.ModelForm):
    class Meta:
        model = TemporaryStudent
        fields = ['name', 'student_img']


class newClassForm(forms.Form):
    name = forms.CharField(max_length=200)

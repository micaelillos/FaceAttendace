from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    username = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'input is-success', 'placeholder': 'Username', 'id': 'hello'}), label='')
    first_name = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'input is-success', 'placeholder': 'First Name', 'id': 'hello'}), label='')

    last_name = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'input is-success', 'placeholder': 'Last Name', 'id': 'hello'}), label='')

    email = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'input is-success', 'placeholder': 'Email', 'id': 'hello'}), label='')

    school_code = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'input is-success', 'placeholder': 'School Code', 'id': 'hello'}), label='')

    teacher_id = forms.EmailField(widget=forms.TextInput(
        attrs={'class': 'input is-success', 'placeholder': 'Teacher id', 'id': 'hello'}), label='')

    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'input is-success',
            'placeholder': 'Password',
            'id': 'hi',
        }
    ), label='')

    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'input is-success',
            'placeholder': 'Password Confirmation',
            'id': 'hi',
        }
    ), label='')

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
        attrs={'class': 'input is-success', 'placeholder': 'Username', 'id': 'hello'}),label='')
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class': 'input is-success',
            'placeholder': 'Password',
            'id': 'hi',
        }
),label='')

class NewStudentForm(forms.Form):
    name = forms.CharField(max_length=200)
    embedding_link = forms.CharField(max_length=200)
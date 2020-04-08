from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from main.form import SignUpForm
from .models import School, Teacher, Student, Class
import json
# Create your views here.
# 68722828


def homepage(request):
    if request.user.is_authenticated:

        teacher = Teacher.objects.filter(username=request.user.username)[0]
        classes = Class.objects.filter(teacher=teacher).all()
        return render(request=request, template_name='main/home.html', context={'classes': classes})
    else:
        form = AuthenticationForm()
        return render(request, 'main/login.html', {'form': form})


def get_Student(request, student_name):
    if request.method == 'GET':
        try:
            student = Student.objects.filter(name=student_name)[0]
            response = json.dumps([{'Student id': student.id, 'Student name': student.name, 'Class': student.origin_class, 'School': str(student.school)}])
        except:
            response = json.dumps([{'Error': 'No Student Found'}])
        return HttpResponse(response, content_type='text/json')


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'new account created: {username}')
            messages.info(request, f'You are now logged in as {username}')
            login(request, user)

            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            name = first_name + ' ' + last_name
            school_code = form.cleaned_data.get('school_code')
            school = School.objects.filter(teacher_code=school_code)[0]
            new_teacher = Teacher(name=name, school=school, username=username)
            new_teacher.save()

            return redirect('main:homepage')
        else:
            for msg in form.error_messages:
                messages.error(request, form.error_messages[msg])
                print('Error')

    form = SignUpForm
    return render(request, 'main/register.html', {'form': form})


def logout_request(request):
    logout(request)
    messages.info(request, 'Logged out successfully')
    return redirect('main:homepage')


def login_request(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged in as {username}')
                return redirect('main:homepage')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')

    form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})


def view_classes(request, teacher_id):
    pass

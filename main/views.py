from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from main.form import SignUpForm
from .models import School, Teacher, Student, Class
import json
# Create your views here.
# teacher: 97641981
# admin: 467713068


def homepage(request):
    if request.user.is_authenticated:

        teacher = Teacher.objects.filter(username=request.user.username)[0]

        if not teacher.is_admin:  # in case its not a school admin
            classes = Class.objects.filter(teacher=teacher).all()
            return render(request=request, template_name='main/home.html', context={'classes': classes})
        else:
            classes = get_dict_of_origin_classes(teacher.school)
            teachers = Teacher.objects.filter(school=teacher.school, is_admin=False).all()
            return render(request=request, template_name='main/admin_home.html',
                          context={'classes': classes, 'teachers': teachers})
    else:
        form = AuthenticationForm()
        return redirect('main:login')


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
            if len(School.objects.filter(teacher_code=school_code).all()) > 0:
                school = School.objects.filter(teacher_code=school_code).all()[0]
                new_teacher = Teacher(name=name, school=school, username=username)
                new_teacher.save()
            elif len(School.objects.filter(admin_code=school_code).all()) > 0:
                school = School.objects.filter(admin_code=school_code).all()[0]
                new_teacher = Teacher(name=name, school=school, username=username, is_admin=True)
                new_teacher.save()
            else:
                print('error')
                # add error: school code not found
                pass

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

    if not request.user.is_authenticated and request.method == 'POST':
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


def view_class(request, class_id):
    if request.user.is_authenticated:

        teacher = Teacher.objects.filter(username=request.user.username)[0]
        class_ = Class.objects.filter(teacher=teacher, id=class_id)[0]
        student_list = class_.get_student_list()
        return render(request=request, template_name='main/view_class.html', context={'student_list': student_list})
    else:
        form = AuthenticationForm()
        return render(request, 'main/login.html', {'form': form})


def view_school(request):
    if request.user.is_authenticated:
        teacher = Teacher.objects.filter(username=request.user.username)[0]
        school = teacher.school
        classes = get_dict_of_origin_classes(school)
        return render(request, 'main/view_school.html', {'classes': classes})

    else:
        form = AuthenticationForm()
        return render(request, 'main/login.html', {'form': form})


def get_dict_of_origin_classes(school):
    students = Student.objects.filter(school=school).all()
    classes = {}
    for student in students:
        key = student.origin_class
        if classes.get(key) is None:
            classes[key] = [student]
        else:
            classes[key].append(student)

    return classes


def get_all_teacher_classes(request, username):
    teacher = Teacher.objects.filter(username=username)[0]
    if request.method == 'GET':
        try:
            classes = Class.objects.filter(teacher=teacher).all()
            class_names = [c.name for c in classes]

            response = json.dumps([{'classes': class_names}])
        except:
            response = json.dumps([{'Error': 'no classes'}])

    return HttpResponse(response, content_type='text/json')


def get_origin_class_list(school, origin_class):
    student_list = Student.objects.filter(school=school, origin_class=origin_class).all()
    return student_list

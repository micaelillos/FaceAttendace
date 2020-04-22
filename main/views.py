from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from main.form import SignUpForm, NewStudentForm, LoginForm
from .models import School, Teacher, Student, Class
import json


# Create your views here.
# teacher: 97641981
# admin: 467713068

def error_404(request, exception):
    data = {}
    return render(request, 'main/hello.html', data)


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
        print(form.is_valid())
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

    form = LoginForm()
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


def view_teacher(request, teacher_id):
    if request.user.is_authenticated:
        teacher = Teacher.objects.filter(id=teacher_id)[0]
        classes = Class.objects.filter(teacher=teacher).all()
        return render(request=request, template_name='main/view_teacher.html',
                      context={'classes': classes, 'teacher': teacher})
    else:
        return redirect('main:login')


def view_student(request, student_id):
    if request.user.is_authenticated:
        student = Student.objects.filter(id=student_id)[0]
        return render(request, 'main/view_student.html', {'student': student})
    else:
        return redirect('main:login')


def view_class(request, class_id):
    if request.user.is_authenticated:

        teacher = Teacher.objects.filter(username=request.user.username)[0]
        class_ = Class.objects.filter(teacher=teacher, id=class_id)[0]
        student_list = class_.get_student_list()
        return render(request=request, template_name='main/view_class.html',
                      context={'student_list': student_list, 'path': '/'})
    else:
        form = AuthenticationForm()
        return render(request, 'main/login.html', {'form': form})


def view_origin_class(request, origin_class):
    if request.user.is_authenticated:
        username = request.user.username
        teacher = Teacher.objects.filter(username=username)[0]
        school = teacher.school
        student_list = Student.objects.filter(school=school, origin_class=origin_class).all()
        return render(request, 'main/view_origin_class.html', {'student_list': student_list,
                                                               'origin_class': origin_class})
    else:
        return redirect('main:login')


def view_teacher_class_for_admin(request, teacher_id, class_id):
    if request.user.is_authenticated:

        teacher = Teacher.objects.filter(id=teacher_id)[0]
        class_ = Class.objects.filter(teacher=teacher, id=class_id)[0]
        student_list = class_.get_student_list()
        return render(request=request, template_name='main/view_class.html',
                      context={'student_list': student_list,
                               'path': '/view_teacher/' + str(teacher_id)})
    else:
        form = AuthenticationForm()
        return render(request, 'main/login.html', {'form': form})


def add_student_to_origin(request, origin_class):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = NewStudentForm(request.POST)
            if form.is_valid():
                username = request.user.username
                teacher = Teacher.objects.filter(username=username)[0]
                school = teacher.school
                name = form.cleaned_data.get('name')
                embedding_link = form.cleaned_data.get('embedding_link')
                new_student = Student(name=name, embedding_link=embedding_link,
                                      origin_class=origin_class, school=school)
                new_student.save()
                # add added student message
                return redirect('main:view origin class', origin_class=origin_class)
            else:
                # add not valid form error
                return render(request, 'main/add_student.html', {'form': form})
        else:
            form = NewStudentForm
            return render(request, 'main/add_student.html', {'form': form})
    else:
        return redirect('main:login')


# help functions
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


def get_origin_class_list(school, origin_class):
    student_list = Student.objects.filter(school=school, origin_class=origin_class).all()
    return student_list




# json functions
def get_Student(request, student_name):
    if request.method == 'GET':
        try:
            student = Student.objects.filter(name=student_name)[0]
            response = json.dumps([{'Student id': student.id, 'Student name': student.name,
                                    'Class': student.origin_class, 'School': str(student.school)}])
        except:
            response = json.dumps([{'Error': 'No Student Found'}])
        return HttpResponse(response, content_type='text/json')


def get_all_teacher_classes(request, username):
    teacher = Teacher.objects.filter(username=username)[0]
    if request.method == 'GET':
        try:
            classes = Class.objects.filter(teacher=teacher).all()
            class_names = [c.name for c in classes]

            response = json.dumps([{'classes': class_names}])
        except:
            response = json.dumps([{'Error': 'no classes'}])
    else:
        response = None
    return HttpResponse(response, content_type='text/json')

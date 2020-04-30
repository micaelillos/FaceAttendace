from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from main.form import SignUpForm, NewStudentForm, LoginForm, newClassForm
from .models import School, Teacher, Student, Class, TemporaryStudent
import json
from django.utils.encoding import force_text
from .face_recognition import save_embedding, face_recognition_init
# Create your views here.
# teacher: 97641981
# admin: 467713068


# Todo in add_student function add a pic slot
# Todo add tables for origin classes and student
# Todo add option to create new class- started need to add check box
# Todo add option to add students to a class


def error_404(request, exception):
    data = {}
    return render(request, 'main/hello.html', data)


def landing_page(request):
    return render(request, 'main/landing_page.html')


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
        return redirect('main:landing page')


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        print(form.is_valid())
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
                print(f'Error: {form.error_messages}')

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

    return redirect('main:landing page')


def view_school(request):
    if request.user.is_authenticated:
        teacher = Teacher.objects.filter(username=request.user.username)[0]
        school = teacher.school
        classes = get_dict_of_origin_classes(school)
        return render(request, 'main/view_school.html', {'classes': classes})

    else:
        return redirect('main:landing page')


def view_teacher(request, teacher_id):
    if request.user.is_authenticated:
        teacher = Teacher.objects.filter(id=teacher_id)[0]
        classes = Class.objects.filter(teacher=teacher).all()
        return render(request=request, template_name='main/view_teacher.html',
                      context={'classes': classes, 'teacher': teacher})
    else:
        return redirect('main:landing page')


def view_student(request, student_id):
    if request.user.is_authenticated:
        student = Student.objects.filter(id=student_id)[0]
        return render(request, 'main/view_student.html', {'student': student})
    else:
        return redirect('main:landing page')


def view_class(request, class_id):
    if request.user.is_authenticated:

        teacher = Teacher.objects.filter(username=request.user.username)[0]
        class_ = Class.objects.filter(teacher=teacher, id=class_id)[0]
        student_list = class_.get_student_list()
        return render(request=request, template_name='main/view_class.html',
                      context={'student_list': student_list, 'path': '/', 'class_id': class_id,
                               'class_name': class_.name})
    else:
        return redirect('main:landing page')


def view_origin_class(request, origin_class):
    if request.user.is_authenticated:
        username = request.user.username
        teacher = Teacher.objects.filter(username=username)[0]
        school = teacher.school
        student_list = Student.objects.filter(school=school, origin_class=origin_class).all()
        return render(request, 'main/view_origin_class.html', {'student_list': student_list,
                                                               'origin_class': origin_class})
    else:
        return redirect('main:landing page')


def view_teacher_class_for_admin(request, teacher_id, class_id):
    if request.user.is_authenticated:

        teacher = Teacher.objects.filter(id=teacher_id)[0]
        class_ = Class.objects.filter(teacher=teacher, id=class_id)[0]
        student_list = class_.get_student_list()
        return render(request=request, template_name='main/view_class.html',
                      context={'student_list': student_list, 'class_name': class_.name,
                               'path': '/view_teacher/' + str(teacher_id), 'class_id': class_.id})
    else:
        return redirect('main:landing page')


def add_student_to_origin(request, origin_class):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = NewStudentForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                face_recognition_init()
                username = request.user.username
                teacher = Teacher.objects.filter(username=username)[0]
                school = teacher.school
                name = form.cleaned_data.get('name')
                image = form.cleaned_data.get('student_img')
                s = TemporaryStudent.objects.filter(name=name)[0]
                image_link = 'media/images/' + str(image)
                embedding_link = 'main/student_embeddings/' + name
                save_embedding(image_link, embedding_link)
                s.delete()

                new_student = Student(name=name, embedding_link=embedding_link,
                                      origin_class=origin_class, school=school)
                new_student.save()

                # add added student message
                return redirect('main:view origin class', origin_class=origin_class)
            else:
                # add not valid form error
                return render(request, 'main/add_student.html', {'form': form})
        else:
            form = NewStudentForm()
            return render(request, 'main/add_student.html', {'form': form})
    else:
        return redirect('main:landing page')


def create_new_class(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = newClassForm(request.POST)

            if form.is_valid():
                teacher = Teacher.objects.filter(username=request.user.username)[0]
                class_name = form.cleaned_data.get('name')
                new_class = Class(name=class_name, teacher=teacher)
                new_class.save()
                return redirect('main:view school for new class', new_class.id)
        else:
            form = newClassForm
            return render(request, 'main/create_new_class.html', {'form': form})
    else:
        return redirect('main:landing page')


def view_school_for_new_class(request, class_id):
    if request.user.is_authenticated:
        teacher = Teacher.objects.filter(username=request.user.username)[0]
        classes = get_dict_of_origin_classes(teacher.school)

        url = str(request.META.get('HTTP_REFERER'))
        button = '0'  # for add
        if 'create_new_class' in url:
            button = '1'  # for Create
        return render(request=request, template_name='main/view_school_for_new_class.html',
                      context={'classes': classes, 'class_id': class_id, 'button': button})
    else:
        return redirect('main:landing page')


def select_students_from_origin(request, button, origin_class, class_id):
    if request.user.is_authenticated:
        username = request.user.username
        teacher = Teacher.objects.filter(username=username)[0]
        school = teacher.school
        student_list = Student.objects.filter(school=school, origin_class=origin_class).all()

        print(request.method)
        if request.method == 'GET':
            return render(request, 'main/select_students_from_origin.html',
                          {'student_list': student_list, 'origin_class': origin_class, 'class_id': class_id,
                           'button': button})
        else:
            wanted = request.POST.getlist('students')
            class_ = Class.objects.filter(id=class_id)[0]
            for student in student_list:
                if student.name in wanted:
                    class_.add_student(student)
            if teacher.is_admin:

                return redirect('main:view teacher class for admin', class_.teacher.id, class_id)
            else:
                return redirect('main:view class', class_id)

    else:
        return redirect('main:landing page')


def new_origin_class(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = newClassForm(request.POST)

            if form.is_valid():
                teacher = Teacher.objects.filter(username=request.user.username)[0]
                school = teacher.school
                class_name = request.POST.getlist('name')[0]
                school.add_origin_class(class_name)

                return redirect('main:admin homepage')
        else:
            form = newClassForm
            return render(request, 'main/create_new_class.html', {'form': form})
    else:
        return redirect('main:landing page')


def delete_class_verification(request, class_id):
    if request.user.is_authenticated:

        teacher = Teacher.objects.filter(username=request.user.username)[0]

        class_ = Class.objects.filter(id=class_id)[0]
        if teacher.school != class_.teacher.school:
            raise Exception('Not allowed to delete this class')
            # will raise error if user tries to delete someone else class

        return render(request=request, template_name='main/delete_class_verification.html',
                      context={'path': '/', 'class_id': class_id, 'class_name': class_.name})
    else:
        return redirect('main:landing page')


def delete_class(request, class_id):
    if request.user.is_authenticated:

        teacher = Teacher.objects.filter(username=request.user.username)[0]
        class_ = Class.objects.filter(id=class_id)[0]
        if teacher.school != class_.teacher.school:
            raise Exception('Not allowed to delete this class')
            # will raise error if user tries to delete someone else class

        class_.delete()
        if teacher.is_admin:
            return redirect('main:view teacher', class_.teacher.id)
        else:
            return redirect('main:homepage')
    else:
        return redirect('main:landing page')


# help functions
def get_dict_of_origin_classes(school):
    students = Student.objects.filter(school=school).all()
    classes = {class_name: [] for class_name in school.get_origin_class_list()}
    for student in students:
        key = student.origin_class
        classes[key].append(student)

    return classes


def get_origin_class_list(school, origin_class):
    student_list = Student.objects.filter(school=school, origin_class=origin_class).all()
    return student_list


# json functions

# Todo json authentication
# Todo json get all students who were in class
# Todo json get all classes for specific teacher


def get_Student(request, student_name):
    if request.method == 'GET':
        try:
            student = Student.objects.filter(name=student_name)[0]
            response = json.dumps([{'Student id': student.id, 'Student name': student.name,
                                    'Class': student.origin_class, 'School': str(student.school)}])
        except:
            response = json.dumps([{'Error': 'No Student Found'}])
        return HttpResponse(response, content_type='text/json')


# Todo change username to id
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

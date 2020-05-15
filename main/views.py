from __future__ import unicode_literals
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from main.form import SignUpForm, NewStudentForm, LoginForm, newClassForm
from .models import School, Teacher, Student, Class, TemporaryStudent, Report
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from random import randint
from .face_recognition import save_embedding, face_recognition_init, find_known_faces
import os
from django.views.decorators.csrf import csrf_exempt
import base64
import pickle


# Create your views here.
# teacher: 33638261
# admin: 154491701
# amir Token: b66b7ade1e3d73b4f6370613f1d447a448531e17
class testView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, jakcob!'}
        return Response(content)


def error_404(request, exception):
    data = {exception}
    return render(request, 'main/hello.html', data)


def landing_page(request):
    return render(request, 'main/landing_page.html')


def homepage(request):
    if request.user.is_authenticated:

        teacher = Teacher.objects.filter(username=request.user.username)[0]

        if not teacher.is_admin:  # in case its not a school admin
            classes = Class.objects.filter(teacher=teacher).all()
            classes = [(c, c.get_attendance_rate()) for c in classes]
            return render(request=request, template_name='main/home.html', context={'classes': classes})
        else:
            classes = get_dict_of_origin_classes(teacher.school)
            teachers = Teacher.objects.filter(school=teacher.school, is_admin=False).all()
            teachers = sorted(teachers, key=lambda x: x.name)

            return render(request=request, template_name='main/admin_home.html',
                          context={'classes': classes, 'teachers': teachers})
    else:
        return redirect('main:landing page')


@api_view(['POST'])
def apiregister(request):
    return


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
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                logout(request)
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
        student_list.sort(key=lambda x: x.origin_class, reverse=True)

        # reports
        reports = Report.objects.filter(belonging_class=class_, status='done')
        if len(reports) > 0:
            reports = sorted(reports, key=lambda x: x.date)
            student_dict = {key: [val] for key, val in reports[0].get_student_dict().items()}
            for i, report in enumerate(reports):
                if i != 0:
                    new_dict = report.get_student_dict()
                    for key, val in new_dict.items():
                        student_dict[key].append(val)

            if len(student_dict) != len(student_list):
                for student in student_list:  # change next: remove .name
                    if student.name not in student_dict:
                        student_dict[student.name] = [False for _ in range(len(reports))]

            student_dict = {key.name: student_dict[key.name] for key in student_list}
            student_list = [(l, int(
                100 * len(list(filter((lambda x: x is True), student_dict[l.name]))) / len(student_dict[l.name]))) for l
                            in student_list]

        else:
            student_dict = {}
            student_list = [(l, 0) for l in student_list]
        return render(request=request, template_name='main/view_class.html',
                      context={'student_list': student_list, 'path': '/', 'class_id': class_id,
                               'class_name': class_.name, 'reports': reports, 'student_dict': student_dict,
                               'num_of_reports': len(reports)
                               })
    else:
        return redirect('main:landing page')


def view_origin_class(request, origin_class):
    if request.user.is_authenticated:
        username = request.user.username
        teacher = Teacher.objects.filter(username=username)[0]
        school = teacher.school
        student_list = Student.objects.filter(school=school, origin_class=origin_class).all()
        student_list = sorted(student_list, key=lambda x: x.name)
        return render(request, 'main/view_origin_class.html', {'student_list': student_list,
                                                               'origin_class': origin_class,
                                                               'is_admin': teacher.is_admin})
    else:
        return redirect('main:landing page')


def view_teacher_class_for_admin(request, teacher_id, class_id):
    if request.user.is_authenticated:

        teacher = Teacher.objects.filter(id=teacher_id)[0]
        class_ = Class.objects.filter(teacher=teacher, id=class_id)[0]
        student_list = class_.get_student_list()
        student_list.sort(key=lambda x: x.origin_class, reverse=True)

        # reports
        reports = Report.objects.filter(belonging_class=class_, status='done')
        if len(reports) > 0:
            reports = sorted(reports, key=lambda x: x.date)
            student_dict = {key: [val] for key, val in reports[0].get_student_dict().items()}
            for i, report in enumerate(reports):
                if i != 0:
                    new_dict = report.get_student_dict()
                    for key, val in new_dict.items():
                        student_dict[key].append(val)

            if len(student_dict) != len(student_list):
                for student in student_list:  # change next: remove .name
                    if student.name not in student_dict:
                        student_dict[student.name] = [False for _ in range(len(reports))]

            student_dict = {key.name: student_dict[key.name] for key in student_list}
            student_list = [(l, int(100 * len(list(filter((lambda x: x is True), student_dict[l.name]))))) for l in
                            student_list]

        else:
            student_dict = {}
            student_list = [(l, 0) for l in student_list]
        return render(request=request, template_name='main/view_class.html',
                      context={'student_list': student_list, 'path': '/', 'class_id': class_id,
                               'class_name': class_.name, 'reports': reports, 'student_dict': student_dict,
                               'num_of_reports': len(reports)
                               })
    else:
        return redirect('main:landing page')


def add_student_to_origin(request, origin_class):
    if request.user.is_authenticated:
        face_recognition_init()
        if request.method == 'POST':
            form = NewStudentForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                username = request.user.username
                teacher = Teacher.objects.filter(username=username)[0]
                school = teacher.school
                name = form.cleaned_data.get('name')
                image = form.cleaned_data.get('student_img')
                s = TemporaryStudent.objects.filter(name=name)[0]
                image_link = 'media/images/' + str(image)
                embedding_link = 'main/student_embeddings/' + name + str(randint(10000, 99999))
                save_embedding(image_link, embedding_link)
                s.delete()
                os.remove(image_link)
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


def view_reports(request, class_id):
    if request.user.is_authenticated:
        class_ = Class.objects.filter(id=class_id)[0]
        reports = Report.objects.filter(belonging_class=class_)
        reports = sorted(reports, key=lambda x: x.date)
        student_dict = {key: [val] for key, val in reports[0].get_student_dict().items()}
        for i, report in enumerate(reports):
            if i != 0:
                new_dict = report.get_student_dict()
                for key, val in new_dict.items():
                    student_dict[key].append(val)
        print(student_dict)
        return render(request, 'main/view_reports.html',
                      context={'reports': reports, 'student_dict': student_dict, 'class_name': class_.name})

    else:
        return redirect('main:landing page')


# help functions
def get_dict_of_origin_classes(school):
    students = Student.objects.filter(school=school).all()
    class_list = school.get_origin_class_list()
    class_list.sort(reverse=True)
    classes = {class_name: [] for class_name in class_list}
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


def get_all_teacher_classes(id):
    teacher = Teacher.objects.filter(id=id)[0]

    try:
        classes = Class.objects.filter(teacher=teacher).all()
        class_details = [[c.name, c.id] for c in classes]

        response = {'classes': class_details}
    except:
        response = {'Error': 'no classes'}

    return response


@csrf_exempt
def api_start_report(request, class_id):
    data = json.loads(request.body.decode("utf-8"))[0]
    token = str(data['token'])
    user = Token.objects.filter(key=token)[0].user
    if user is None:
        response = json.dumps([{'Error': 'no such token'}])
        return HttpResponse(response, content_type='text/json')

    teacher = Teacher.objects.filter(username=str(user))[0]
    class_ = Class.objects.filter(id=class_id, teacher=teacher)[0]

    problematic_reports = Report.objects.filter(belonging_class=class_, status='constructing').all()
    for problematic_report in problematic_reports:
        problematic_report.delete()

    name_list = [student.name for student in class_.get_student_list()]
    report = Report(belonging_class=class_, status='constructing')
    report.create_student_dict(name_list)
    report.save()

    response = json.dumps([{'sent': 'received'}])
    return HttpResponse(response, content_type='text/json')


@csrf_exempt
def receive_class_img(request, class_id):
    print('start')
    data = json.loads(request.body.decode("utf-8"))[0]
    token = str(data['token'])
    user = Token.objects.filter(key=token)[0].user
    if user is None:
        response = json.dumps([{'Error': 'no such token'}])
        return HttpResponse(response, content_type='text/json')

    teacher = Teacher.objects.filter(username=str(user))[0]
    data = str(data['img'])
    if data[:4] == 'data':
        data = data[23:]
    img = bytes(data, encoding="utf-8")
    # send without prefix
    filename = "main/imageToSave.jpg"
    with open(filename, "wb") as fh:
        fh.write(base64.decodebytes(img))

    class_ = Class.objects.filter(id=class_id, teacher=teacher)[0]
    name_list = []
    embedding_list = []
    for student in class_.get_student_list():
        name_list.append(student.name)
        link = student.embedding_link
        file = open(link, 'rb')
        embedding = pickle.load(file)
        file.close()
        embedding_list.append(embedding)

    present_list = find_known_faces(embedding_list, name_list, filename)
    print(f'present_list: {type(present_list)}')

    report = Report.objects.filter(belonging_class=class_, status='constructing')[0]
    report.add_students(present_list)
    report.save()
    print(present_list)
    response = json.dumps([{'success': 'received image'}])
    return HttpResponse(response, content_type='text/json')


@csrf_exempt
def api_finish_report(request, class_id):
    data = json.loads(request.body.decode("utf-8"))[0]
    token = str(data['token'])
    user = Token.objects.filter(key=token)[0].user
    if user is None:
        response = json.dumps([{'Error': 'no such token'}])
        return HttpResponse(response, content_type='text/json')

    teacher = Teacher.objects.filter(username=str(user))[0]
    class_ = Class.objects.filter(id=class_id, teacher=teacher)[0]
    report = Report.objects.filter(belonging_class=class_, status='constructing')[0]
    report.change_status('done')
    response = json.dumps([{'present dict': report.get_student_dict()}])
    return HttpResponse(response, content_type='text/json')


@csrf_exempt
def api_login(request):
    data = json.loads(request.body.decode("utf-8"))[0]
    user = authenticate(username=data['username'], password=data['password'])

    if user is None:
        response = json.dumps([{'Error': 'no user found'}])
        return HttpResponse(response, content_type='text/json')

    print(user)
    try:
        teacher = Teacher.objects.filter(username=user.username)[0]
        response = json.dumps([{'token': str(Token.objects.filter(user=user)[0])},
                               {'classes': get_all_teacher_classes(teacher.id)}])

    except IndexError:
        response = json.dumps([{'Error': 'no token registered'}])

    return HttpResponse(response, content_type='text/json')
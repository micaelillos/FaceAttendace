from django.db import models
from django.contrib.auth.models import User
from random import randint
import pickle
import ast
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


class School(models.Model):
    name = models.CharField(max_length=200)
    id = models.AutoField(primary_key=True)
    teacher_code = models.CharField(max_length=8, unique=True, blank=True,
                                    default=str(randint(10000000, 99999999)))
    admin_code = models.CharField(max_length=9, unique=True, blank=True,
                                  default=str(randint(100000000, 999999999)))
    origin_class_list = models.CharField(max_length=2000, default='', blank=True)

    def add_origin_class(self, origin_class):
        if origin_class not in self.get_origin_class_list():
            current = str(self.origin_class_list)
            current += str(origin_class) + ' '
            self.origin_class_list = current
            self.save()
        else:
            print('Origin class already created')

    def get_origin_class_list(self):
        origin_list = []
        l = str(self.origin_class_list)
        class_name = ''
        for i, _ in enumerate(l):
            if l[i] != ' ':
                class_name += l[i]
            else:
                origin_list.append(class_name)
                class_name = ''

        if class_name != ' ' and class_name != '':
            origin_list.append(class_name)

        return origin_list

    def __str__(self):
        return self.name

    def _delete_origin_class(self, origin_class):
        oc_list = self.get_origin_class_list()
        self.origin_class_list = ''
        for oc in oc_list:
            if oc != origin_class:
                self.add_origin_class(oc)


class Teacher(models.Model):
    username = models.CharField(max_length=200, default='not set yet')
    name = models.CharField(max_length=200)
    id = models.AutoField(primary_key=True)
    is_admin = models.BooleanField(default=False)
    school = models.ForeignKey(School, default=0, on_delete=models.SET_DEFAULT)

    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=200)
    id = models.AutoField(primary_key=True)
    embedding_link = models.CharField(max_length=200)
    origin_class = models.CharField(max_length=10)
    school = models.ForeignKey(School, default=0, on_delete=models.SET_DEFAULT)

    def __str__(self):
        return self.name


class Class(models.Model):
    name = models.CharField(max_length=200)

    id = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Teacher, default=0, on_delete=models.SET_DEFAULT)
    student_list = models.CharField(max_length=1000, default='', blank=True)

    class Meta:
        verbose_name_plural = 'Classes'

    def __str__(self):
        return self.name

    def add_student(self, student):
        if student not in self.get_student_list():
            current = str(self.student_list)
            print(current)
            current += str(student.id) + ' '
            self.student_list = current
            self.save()
        else:
            print('Student already in class')

    def get_student_list(self):
        student_list = []
        l = str(self.student_list)
        student_id = ''
        for i, _ in enumerate(l):
            if l[i] != ' ':
                student_id += l[i]
            else:
                student_list.append(Student.objects.filter(id=student_id)[0])
                student_id = ''
        if student_id != ' ' and student_id != '':
            student_list.append(Student.objects.filter(id=student_id)[0])

        return student_list

    def get_class_embeddings(self):
        student_list = self.get_student_list()
        embeddings = []
        names = []
        for student in student_list:
            file = open(student.embedding_link, 'rb')
            embedding = pickle.load(file)
            embeddings.append(embedding)
            names.append(student.name)
            file.close()

        return embeddings, names

    def get_student_count(self):
        return len(self.get_student_list())

    def get_attendance_rate(self):
        reports = Report.objects.filter(belonging_class=self)
        if reports:
            true_count, count_sum = 0, 0

            for report in reports:
                s_dict = report.get_student_dict()
                for _, val in s_dict.items():
                    if val:
                        true_count += 1
                    count_sum += 1

            return int(100 * true_count / count_sum)
        else:
            return 0


class TemporaryStudent(models.Model):
    name = models.CharField(max_length=200)
    student_img = models.ImageField(upload_to='images/')


class Report(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateField(auto_now_add=True)
    belonging_class = models.ForeignKey(Class, default=0, on_delete=models.SET_DEFAULT)
    dictionary = models.CharField(max_length=1000)

    def get_student_dict(self):
        return ast.literal_eval(str(self.dictionary))

    def create_student_dict(self, all_names, present_names):
        d = {}
        for student in all_names:
            if student in present_names:
                d[student] = True
            else:
                d[student] = False

        self.dictionary = str(d)
        self.save()

    def change_student_dict(self, name, new_val):
        d = self.get_student_dict()
        d[name] = new_val
        self.dictionary = str(d)
        self.save()

    class Meta:
        verbose_name_plural = 'Reports'


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

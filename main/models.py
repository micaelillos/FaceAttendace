from django.db import models
from django.contrib.auth.models import User
from random import randint
import pickle
import ast

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



class TemporaryStudent(models.Model):
    name = models.CharField(max_length=200)
    student_img = models.ImageField(upload_to='images/')

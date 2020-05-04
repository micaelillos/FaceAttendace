from django.contrib import admin

from .models import School, Teacher, Student, Class, Report, TemporaryStudent

# Register your models here.

admin.site.register(School)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Class)
admin.site.register(Report)
admin.site.register(TemporaryStudent)
"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('admin_home', views.homepage, name='admin homepage'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_request, name='logout'),
    path('login/', views.login_request, name='login'),
    path('view_class/<int:class_id>/', views.view_class, name='view class'),
    path('view_origin_class/<str:origin_class>/', views.view_origin_class, name='view origin class'),
    path('view_school/', views.view_school, name='view school'),
    path('view_teacher/<int:teacher_id>/', views.view_teacher, name='view teacher'),
    path('view_student/<int:student_id>/', views.view_student, name='view student'),
    path('view_teacher_class_for_admin/<int:teacher_id>/<int:class_id>/', views.view_teacher_class_for_admin, name='view teacher class for admin'),
    path('add_student/<str:origin_class>/', views.add_student_to_origin, name='add student to origin class'),

    # Json response
    path('student/<str:student_name>', views.get_Student, name='get student'),
    path('teacher/<str:username>', views.get_all_teacher_classes, name='get all teacher classes'),

]

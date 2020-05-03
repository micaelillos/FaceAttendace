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
from django.urls import path, include
from django.contrib import admin
from main import views as myapp_views
from mysite import settings
from . import views
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static

app_name = 'main'

urlpatterns = [
    path('welcome', views.landing_page, name='landing page'),
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
    path('view_teacher_class_for_admin/<int:teacher_id>/<int:class_id>/', views.view_teacher_class_for_admin,
         name='view teacher class for admin'),
    path('add_student/<str:origin_class>/', views.add_student_to_origin, name='add student to origin class'),
    path('view_school_for_new_class/<str:class_id>/', views.view_school_for_new_class,
         name='view school for new class'),
    path('select_students_from_origin/<str:button>/<str:origin_class>/<str:class_id>/',
         views.select_students_from_origin, name='select students from origin'),
    path('create_new_class/', views.create_new_class, name='create new class'),
    path('new_origin_class/', views.new_origin_class, name='new origin class'),
    path('delete_class_verification/<str:class_id>/', views.delete_class_verification,
         name='delete class verification'),
    path('delete_class/<str:class_id>/', views.delete_class, name='delete class'),

    # Json response
    path('api/student/<str:student_name>', views.get_Student, name='get student'),
    path('api/teacher/<str:id>', views.get_all_teacher_classes, name='get all teacher classes'),
]
# handler 404
handler404 = myapp_views.error_404

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

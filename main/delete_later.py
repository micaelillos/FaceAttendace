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



class testView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, jakcob!'}
        return Response(content)


@api_view(['POST'])
def apiregister(request):
    return


@csrf_exempt
def api_login(request):
    data = json.loads(request.body.decode("utf-8"))[0]
    user = authenticate(username=data['username'], password=data['password'])
    if user is None:
        response = json.dumps([{'Error': 'no user found'}])
        return HttpResponse(response, content_type='text/json')

    print(user)
    try:
        response = json.dumps([{'Success': str(Token.objects.filter(user=user)[0])}])
    except IndexError:
        response = json.dumps([{'Error': 'no token registered'}])
    return HttpResponse(response, content_type='text/json')

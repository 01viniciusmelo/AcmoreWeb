import base64
import hashlib

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import auth

from apps.account.models import User
from apps.user.models.OldUser import OldUser


def index(request):
    return render(request, 'base.html')

def thanks(request):
    return render(request, 'thanks.html')

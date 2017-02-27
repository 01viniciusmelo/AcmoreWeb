import base64
import hashlib

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import auth
from django.views.decorators.cache import cache_page

from judge.settings import BASE_DIR

import json


def index(request):
    return render(request, 'base.html')

def thanks(request):
    return render(request, 'thanks.html')

def help(request):
    return render(request, 'help.html')

def marquee_message(request):
    with open(BASE_DIR+'/msg.txt', 'r') as msg_file:
        message_content = msg_file.read()

    return HttpResponse(message_content)

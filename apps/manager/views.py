from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse
from apps.account.models import User
import json


def change_password(request):
    if request.user.is_superuser:
        if request.method == 'GET':
            return render(request, 'manage/change-password.html', context={})
        else:

            username = request.POST.get('u')
            password = request.POST.get('p')
            res = {
                'status': 200
            }
            try:
                user = User.objects.get(username=username)
                if user.is_superuser:
                    res['status'] = 403
                    res['message'] = 'User %s is a superuser.' % username
                else:
                    user.set_password(password)
                    user.save()

            except User.DoesNotExist:
                res['status'] = 400
                res['message'] = 'No such User'

            return JsonResponse(res)
    else:
        return HttpResponse('error')


def check_user(request):
    username = request.POST.get('u')
    res = {
        'status':200
    }
    try:
        user = User.objects.get(username=username)
        if user.is_superuser:
            res['status'] = 403
            res['message'] = 'User %s is a superuser.' % username
        res['data'] = {
            'username':user.username,
            'last_login':user.last_login,
            'email':user.email,
        }
    except User.DoesNotExist:
        res['status'] = 400
        res['message'] = 'No such User'

    return JsonResponse(res)


def manage_center(request):
    return render(request, 'manage/manage-center.html', context={})


from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder
from django.core.mail import EmailMessage

from apps.account.models import User
from apps.user.models.OldUser import OldUser

import base64
import hashlib
import json
import shortuuid


def login(request):
    def login_error(from_url, username, type=0):
        types = [
            'Wrong password.',
            'No such user.'
        ]
        context = dict(
            from_url=from_url,
            username=username,
            error_message=types[type],
        )

        return render(request, "login-form.html", context=context)

    if request.method == 'GET':
        from_url = request.GET.get('from_url', reverse('index'))
        if request.user.is_authenticated():
            return HttpResponseRedirect(from_url)

        context = dict(
            from_url=from_url
        )
        return render(request, "login-form.html", context=context)
    else:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        from_url = request.POST.get('from_url', reverse('index'))
        if from_url == '':
            pass
            #from_url = reverse('index')

        if not OldUser.objects.filter(user_id=username).exists():
            return login_error(from_url, '', 1)

        old_user = OldUser.objects.get(user_id=username)


        if not User.objects.filter(username=username).exists():
            salt = base64.decodestring(old_user.password)[20:]

            password_md5 = hashlib.md5(password).hexdigest()
            password_sha1 = hashlib.sha1(password_md5 + salt).digest()

            input_password = base64.b64encode(password_sha1 + salt)

            if old_user.password == input_password:
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    email=old_user.email,
                    is_email_check=0,
                    u_info=old_user,
                )
                user.save()

                #print "new user"
            else:
                return login_error(from_url, username)

        user = auth.authenticate(username=username, password=password)
        #print user
        if user and user.is_active:
            auth.login(request, user)
            #print from_url
            return HttpResponseRedirect(from_url)
        else:
            return login_error(from_url, username)


def register(request):
    def register_error(from_url, username, type=0):
        types = [
            u'Please visit the page in the correct way.',
            u'Some error happened.',
            u'Username has been used.',
            u'E-mail has been used.',
            u'Username not in format.',
            u'Password is too weak.',
            u'Password is different to confirm password.'
        ]
        context = dict(
            from_url=from_url,
            username=username,
            error_message=types[type],
        )

        return render(request, "register-form.html", context=context)

    if request.method == 'GET':
        from_url = request.GET.get('from_url', reverse('index'))

        context = dict(
            from_url=from_url
        )
        return render(request, "register-form.html", context=context)
    else:
        username = request.POST.get('username', False)
        email = request.POST.get('email', False)
        password = request.POST.get('password', False)
        repassword = request.POST.get('repassword', False)

        from_url = request.POST.get('from_url', reverse('index'))
        if from_url == '':
            pass
            #from_url = reverse('index')


        if  username and email and password and repassword:
            if len(username) < 6:
                return register_error(from_url, '', 4)
            if len(password) < 6:
                return register_error(from_url, '', 5)

            if password != repassword:
                return register_error(from_url, '', 6)

            if OldUser.objects.filter(user_id=username).exists() \
                    or User.objects.filter(username=username).exists():
                return register_error(from_url, '', 2)
            if OldUser.objects.filter(email=email).exists() \
                    or User.objects.filter(email=email).exists():
                return register_error(from_url, '', 3)


            old_user = OldUser(
                user_id=username,
                email=email,
                volume=1,
                language=1,
            )
            old_user.save()

            user = User.objects.create_user(
                username=username,
                email=email,
                is_email_check=0,
                password=password,
                is_active=1,
                u_info=old_user
            )
            user.save()
        else:
            return register_error(from_url, '', 0)

        user = auth.authenticate(username=username, password=password)

        #print user
        if user and user.is_active:
            auth.login(request, user)
            #print(from_url)
            return HttpResponseRedirect(from_url)
        else:
            return register_error(from_url, '', 1)


def register_check(request):
    context = dict(
        status=400
    )
    if request.is_ajax() and request.method == "POST":
        check_type = request.POST.get('type', False)
        check_value = request.POST.get('content', False)

        try:
            if check_type and check_value:
                if check_type == 'un':
                    context['data'] = dict(
                        showCheck=1,
                        showMessage=1,
                        check=0,
                        message=u'Username has been used'
                    )
                    OldUser.objects.get(user_id=check_value)
                elif check_type == 'em':
                    context['data'] = dict(
                        showCheck=1,
                        showMessage=1,
                        check=0,
                        message=u'Email has been used'
                    )
                    OldUser.objects.get(email=check_value)
        except OldUser.DoesNotExist:
            context['status'] = 200
            context['message'] = 'OK'
            context['data'] = dict(
                showCheck=1,
                showMessage=0,
                check=1,
                message='OK'
            )

        except OldUser.MultipleObjectsReturned:
            pass

    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")


@login_required(redirect_field_name='from_url')
def check_email(request):
    context = dict(
        status=400
    )
    if request.is_ajax() and request.method == "POST":
        user_id = request.POST.get('user', False)
        if user_id and user_id == request.user.username:
            user = User.objects.get(username=user_id)
            verify_code = shortuuid.uuid()[:6]

            template = u'<div style="font-size: 16px;">Your verification code is:<div style="color: #c12e2a">' \
                       u'<b>'+ verify_code + u'</b>' \
                       u'</div><br>Do not tell anyone this verification code! Please don\'t reply to this email.</div>'

            try:
                email = EmailMessage('ACMORE verify email', template, to=[user.email])
                email.content_subtype = "html"
                if email.send() == 1:
                    request.session['verify_code'] = verify_code

                    context = dict(
                        status=200,
                        message=u'ok'
                    )
                else:
                    context = dict(
                        status=500,
                        message=u'Sorry, Email Server error.'
                    )
            except:
                context = dict(
                    status=500,
                    message=u'Sorry, Unknown error happened.'
                )
        elif 'code' in request.POST:
            context = dict(
                status=400,
                message=u'Sorry, not found this verification code.'
            )
            check_code = request.POST.get('code', False)
            if check_code:
                if 'verify_code' in request.session:
                    if request.session['verify_code'] == check_code:
                        user = User.objects.get(username=request.user.username)
                        user.is_email_check = 1
                        user.save()

                        context = dict(
                            status=200,
                            message=u'ok'
                        )
                    else:
                        context = dict(
                            status=400,
                            message=u'Sorry, verification code already expired, please get new one.'
                        )
        else:
            context = dict(
                status=400,
                message=u'error request'
            )

    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")


@login_required(redirect_field_name='from_url')
def modify_information(request):
    context = dict(
        status=200,
        message=u'OK'
    )
    action = request.POST.get('action', False)
    user = User.objects.get(username=request.user.username)
    if action:
        context['method'] = action
        if action == 'school':
            school = request.POST.get('school', False)
            if school:
                user.u_info.school = school
                user.u_info.save()
        elif action == 'firstName':
            first_name = request.POST.get('firstName', False)
            if first_name:
                user.first_name = first_name
                user.save()
        elif action == 'lastName':
            last_name = request.POST.get('lastName', False)
            if last_name:
                user.last_name = last_name
                user.save()
        elif action == 'nick':
            nick = request.POST.get('nick', False)
            if nick:
                user.u_info.nick = nick
                user.u_info.save()
        elif action == 'password':
            new_password = request.POST.get('new_password', False)
            re_new_password = request.POST.get('re_new_password', False)
            if new_password and re_new_password and new_password == re_new_password and len(new_password) >= 6:
                old_password = request.POST.get('old_password', '')
                user_auth = auth.authenticate(username=request.user.username, password=old_password)
                if user_auth is not None and user_auth.is_active:
                    user.set_password(new_password)
                    user.save()
                else:
                    context = dict(
                        status=204,
                        message=u'Old password error.'
                    )
            else:
                context = dict(
                    status=204,
                    message=u'New password is not received or Entered passwords differ! '
                )
        elif action == 'email':
            if not request.user.is_email_check:
                email = request.POST.get('email', False)
                if email:
                    if User.objects.filter(email=email).exists():
                        context = dict(
                            status=400,
                            message=u'This Email address is already in used.'
                        )
                    else:
                        user.email = email
                        user.save()

                        context = dict(
                            status=200,
                            message=u'modify success.'
                        )
            else:
                context = dict(
                    status=204,
                    message=u'Email already verified.'
                )
        else:
            context = dict(
                status=400,
               message=u'no such action.'
            )
    else:
        context = dict(
            status=405,
            message=u'error request.'
        )


    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")


def logout(request):
    auth.logout(request)

    from_url = request.GET.get('from_url')
    if from_url == '' or from_url == reverse('account_login'):
        from_url = reverse('index')
    return HttpResponseRedirect(from_url)



@login_required(redirect_field_name='from_url')
def user_center(request):
    user = request.user
    if user.u_info.user_id == user.username:

        context = dict()
        return render(request, 'user-center.html', context=context)
    else:
        return render(request, 'error.html')








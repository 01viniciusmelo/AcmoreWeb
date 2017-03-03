from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.user.models.OldUser import OldUser
from django.contrib import admin


class User(AbstractUser):
    is_email_check = models.IntegerField()
    u_info = models.OneToOneField(OldUser)

admin.site.register(User)

class Privilege(models.Model):
    user_id = models.CharField(max_length=48)
    rightstr = models.CharField(max_length=30)
    defunct = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'privilege'

class Loginlog(models.Model):
    user_id = models.CharField(max_length=48)
    password = models.CharField(max_length=40, blank=True, null=True)
    ip = models.CharField(max_length=100, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loginlog'

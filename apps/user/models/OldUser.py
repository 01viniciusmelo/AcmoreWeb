from django.db import models


class OldUser(models.Model):
    user_id = models.CharField(primary_key=True, max_length=48)
    email = models.CharField(max_length=100, blank=True, null=True)
    submit = models.IntegerField(blank=True, null=True)
    solved = models.IntegerField(blank=True, null=True)
    defunct = models.CharField(max_length=1)
    ip = models.CharField(max_length=20)
    accesstime = models.DateTimeField(blank=True, null=True)
    volume = models.IntegerField()
    language = models.IntegerField()
    password = models.CharField(max_length=32, blank=True, null=True)
    reg_time = models.DateTimeField(blank=True, null=True)
    nick = models.CharField(max_length=100)
    school = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'users'


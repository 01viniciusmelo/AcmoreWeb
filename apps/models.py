from __future__ import unicode_literals

from django.db import models


'''
class Contest(models.Model):
    contest_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    defunct = models.CharField(max_length=1)
    description = models.TextField(blank=True, null=True)
    private = models.IntegerField()
    langmask = models.IntegerField()
    password = models.CharField(max_length=16)

    class Meta:
        managed = False
        db_table = 'contest'


class ContestProblem(models.Model):
    problem_id = models.IntegerField()
    contest_id = models.IntegerField(blank=True, null=True)
    title = models.CharField(max_length=200)
    num = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'contest_problem'


class Custominput(models.Model):
    solution_id = models.IntegerField(primary_key=True)
    input_text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'custominput'



class Mail(models.Model):
    mail_id = models.AutoField(primary_key=True)
    to_user = models.CharField(max_length=48)
    from_user = models.CharField(max_length=48)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)
    new_mail = models.IntegerField()
    reply = models.IntegerField(blank=True, null=True)
    in_date = models.DateTimeField(blank=True, null=True)
    defunct = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'mail'


class News(models.Model):
    news_id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=48)
    title = models.CharField(max_length=200)
    content = models.TextField()
    time = models.DateTimeField()
    importance = models.IntegerField()
    defunct = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'news'


class Online(models.Model):
    hash = models.CharField(primary_key=True, max_length=32)
    ip = models.CharField(max_length=20)
    ua = models.CharField(max_length=255)
    refer = models.CharField(max_length=255, blank=True, null=True)
    lastmove = models.IntegerField()
    firsttime = models.IntegerField(blank=True, null=True)
    uri = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'online'

class Privilege(models.Model):
    user_id = models.CharField(max_length=48)
    rightstr = models.CharField(max_length=30)
    defunct = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'privilege'

class Reply(models.Model):
    rid = models.AutoField(primary_key=True)
    author_id = models.CharField(max_length=48)
    time = models.DateTimeField()
    content = models.TextField()
    topic_id = models.IntegerField()
    status = models.IntegerField()
    ip = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'reply'
'''

class Sim(models.Model):
    s_id = models.IntegerField(primary_key=True)
    sim_s_id = models.IntegerField(blank=True, null=True)
    sim = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sim'

'''
class Topic(models.Model):
    tid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=60)
    status = models.IntegerField()
    top_level = models.IntegerField()
    cid = models.IntegerField(blank=True, null=True)
    pid = models.IntegerField()
    author_id = models.CharField(max_length=48)

    class Meta:
        managed = False
        db_table = 'topic'
'''
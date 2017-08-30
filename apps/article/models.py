from __future__ import unicode_literals

from django.db import models
from apps.account.models import User


class Article(models.Model):
    tid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=60)
    content = models.TextField()
    status = models.IntegerField()
    top_level = models.IntegerField()
    cid = models.IntegerField(blank=True, null=True)
    pid = models.IntegerField()
    author = models.ForeignKey(User)
    ip = models.CharField(max_length=32, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'topic'


class Reply(models.Model):
    rid = models.AutoField(primary_key=True)
    author = models.ForeignKey(User)
    #author_username = models.CharField(max_length=64, )
    to_user = models.ForeignKey(User, null=True, related_name='to_user')
    time = models.DateTimeField()
    content = models.TextField()
    topic = models.ForeignKey(Article)
    to_reply = models.ForeignKey('self', null=True)
    status = models.IntegerField()
    ip = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'reply'

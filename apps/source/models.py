from __future__ import unicode_literals
from django.db import models


class OnlySourceCode(models.Model):
    uuid = models.CharField(max_length=22, primary_key=True)
    poster = models.CharField(max_length=255)
    source = models.TextField(blank=True, null=True)
    lexer = models.CharField(max_length=20)
    style = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'only_source_code'


class OjSourceCode(models.Model):
    solution_id = models.AutoField(primary_key=True)
    source = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'source_code_user'

class SourceCode(models.Model):
    solution_id = models.IntegerField(primary_key=True)
    source = models.TextField()

    class Meta:
        managed = False
        db_table = 'source_code'


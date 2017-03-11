from __future__ import unicode_literals
from django.db import models
from django.contrib import admin


class Problem(models.Model):
    rec_id = models.AutoField(primary_key=True)
    problem_id = models.CharField(max_length=48)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    input = models.TextField(blank=True, null=True)
    output = models.TextField(blank=True, null=True)
    sample_input = models.TextField(blank=True, null=True)
    sample_output = models.TextField(blank=True, null=True)
    spj = models.CharField(max_length=1)
    hint = models.TextField(blank=True, null=True)
    source = models.CharField(max_length=200, blank=True, null=True)
    in_date = models.DateTimeField(blank=True, null=True)
    time_limit = models.CharField(max_length=48)
    memory_limit = models.CharField(max_length=48)
    defunct = models.CharField(max_length=1)
    accepted = models.IntegerField(blank=True, null=True)
    submit = models.IntegerField(blank=True, null=True)
    solved = models.IntegerField(blank=True, null=True)
    judge_name = models.CharField(max_length=48)
    attrs = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'problem'

admin.site.register(Problem)
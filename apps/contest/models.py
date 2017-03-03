from __future__ import unicode_literals
from django.db import models


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
    show_rank = models.CharField(max_length=1)

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
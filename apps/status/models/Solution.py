from django.db import models


class Solution(models.Model):
    solution_id = models.AutoField(primary_key=True)
    problem_rec_id = models.IntegerField()
    problem_id = models.IntegerField()
    user_id = models.CharField(max_length=48)
    time = models.IntegerField()
    memory = models.IntegerField()
    in_date = models.DateTimeField()
    result = models.SmallIntegerField()
    result_name = models.CharField(max_length=64)
    language = models.IntegerField()
    language_name = models.CharField(max_length=48)
    ip = models.CharField(max_length=15)
    contest_id = models.IntegerField(blank=True, null=True)
    valid = models.IntegerField()
    num = models.IntegerField()
    code_length = models.IntegerField()
    judgetime = models.DateTimeField(blank=True, null=True)
    pass_rate = models.DecimalField(max_digits=7, decimal_places=6)
    lint_error = models.IntegerField()
    judger = models.CharField(max_length=16)
    judge_type = models.IntegerField()
    judge_name = models.CharField(max_length=48)

    class Meta:
        managed = False
        db_table = 'solution'


class RunTimeInfo(models.Model):
    solution_id = models.AutoField(primary_key=True)
    error = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'runtimeinfo'


class CompileInfo(models.Model):
    solution_id = models.AutoField(primary_key=True)
    error = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'compileinfo'

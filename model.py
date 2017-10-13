# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class AccountUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    is_email_check = models.IntegerField()
    u_info_id = models.CharField(unique=True, max_length=48)

    class Meta:
        managed = False
        db_table = 'account_user'


class AccountUserGroups(models.Model):
    user_id = models.IntegerField()
    group_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'account_user_groups'
        unique_together = (('user_id', 'group_id'),)


class AccountUserUserPermissions(models.Model):
    user_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'account_user_user_permissions'
        unique_together = (('user_id', 'permission_id'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group_id = models.IntegerField()
    permission_id = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group_id', 'permission_id'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type_id', 'codename'),)


class Compileinfo(models.Model):
    solution_id = models.IntegerField(primary_key=True)
    error = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'compileinfo'


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


class Custominput(models.Model):
    solution_id = models.IntegerField(primary_key=True)
    input_text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'custominput'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class JudgeLanguage(models.Model):
    language_id = models.IntegerField()
    language_name = models.CharField(max_length=48)
    enabled = models.IntegerField()
    judge_name = models.CharField(max_length=48)

    class Meta:
        managed = False
        db_table = 'judge_language'


class Loginlog(models.Model):
    user_id = models.CharField(max_length=48)
    password = models.CharField(max_length=40, blank=True, null=True)
    ip = models.CharField(max_length=100, blank=True, null=True)
    time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'loginlog'


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


class OnlySourceCode(models.Model):
    uuid = models.CharField(primary_key=True, max_length=22)
    poster = models.CharField(max_length=255)
    source = models.TextField(blank=True, null=True)
    lexer = models.CharField(max_length=20)
    style = models.CharField(max_length=15)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'only_source_code'


class Privilege(models.Model):
    user_id = models.CharField(max_length=48)
    rightstr = models.CharField(max_length=30)
    defunct = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'privilege'


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
    source = models.CharField(max_length=1000, blank=True, null=True)
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


class Runtimeinfo(models.Model):
    solution_id = models.IntegerField(primary_key=True)
    error = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'runtimeinfo'


class Sim(models.Model):
    s_id = models.IntegerField(primary_key=True)
    sim_s_id = models.IntegerField(blank=True, null=True)
    sim = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sim'


class Solution(models.Model):
    solution_id = models.AutoField(primary_key=True)
    problem_rec_id = models.IntegerField()
    problem_id = models.IntegerField()
    user_id = models.CharField(max_length=48)
    time = models.IntegerField()
    memory = models.IntegerField()
    in_date = models.DateTimeField()
    result = models.SmallIntegerField()
    result_name = models.CharField(max_length=64, blank=True, null=True)
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
    oi_result = models.CharField(max_length=50, blank=True, null=True)
    judge_type = models.IntegerField()
    judge_name = models.CharField(max_length=48)
    vjudge_solution_id = models.CharField(max_length=48, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'solution'


class SourceCode(models.Model):
    solution_id = models.IntegerField(primary_key=True)
    source = models.TextField()

    class Meta:
        managed = False
        db_table = 'source_code'


class SourceCodeUser(models.Model):
    solution_id = models.IntegerField(primary_key=True)
    source = models.TextField()

    class Meta:
        managed = False
        db_table = 'source_code_user'


class Topic(models.Model):
    tid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=60)
    content = models.TextField()
    status = models.IntegerField()
    top_level = models.IntegerField()
    cid = models.IntegerField(blank=True, null=True)
    pid = models.IntegerField()
    author_id = models.CharField(max_length=48)
    ip = models.CharField(max_length=32, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'topic'


class Users(models.Model):
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


class VjudgeUser(models.Model):
    username = models.CharField(max_length=48)
    password = models.CharField(max_length=48)
    judge_name = models.CharField(max_length=48)
    using = models.IntegerField()
    run_id = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vjudge_user'

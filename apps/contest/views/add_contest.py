from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render

from apps.contest.models import Contest
from apps.contest.models import ContestProblem
from apps.problem.models.Problem import Problem as OJproblem
from apps.account.models import Privilege

from datetime import datetime
import json


@login_required(redirect_field_name='from_url')
def create_contest(request):

    context = dict()
    return render(request, 'create-contest.html', context=context)

@login_required
def check_problem(request):
    judge_name = request.POST.get('judge_name', 'LOCAL')
    problem_id = request.POST.get('problemID', 1000)

    try:
        problem_id = int(problem_id)
    except ValueError:
        return HttpResponse('error')

    response = dict(
        status=400
    )
    try:
        problem = OJproblem.objects.values('rec_id','problem_id', 'title').filter(judge_name=judge_name).filter(problem_id=problem_id).get()
        response = dict(
            status=200,
            message='success',
            problem=problem
        )
    except OJproblem.DoesNotExist:
        response['message'] = 'problem with ID ' + str(problem_id) + ' not found.'

    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json")

@login_required
def submit_contest(request):
    response = dict(
        status=400,
        message='request error'
    )
    if request.method == 'POST':
        try:
            data = json.loads(request.POST.get('data'))
            contest = Contest(
                title=data['title'],
                start_time=timezone.make_aware(datetime.strptime(data['startTime'], "%a, %d %b %Y %H:%M:%S %Z"), timezone.get_current_timezone()),
                end_time=timezone.make_aware(datetime.strptime(data['endTime'], "%a, %d %b %Y %H:%M:%S %Z"), timezone.get_current_timezone()),
                defunct='N',
                description=data['desc'],
                private=data['permission'],
                password=data['password'],
                show_rank=data['showRank'],
                langmask=0
            )

            contest.save()

            for index, problem in enumerate(data['problems']):
                _problem = ContestProblem(
                    title=problem['alias'],
                    problem_id=problem['id'],
                    contest_id=contest.contest_id,
                    num=index
                )
                _problem.save()

            privilege = Privilege(
                user_id=request.user.username,
                rightstr='m'+str(contest.contest_id),
                defunct='N'
            )
            privilege.save()

            response = dict(
                status=200,
                message='success',
                contest_id=contest.contest_id
            )
        except:
            response['message'] = 'server error, please retry'

    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json")





















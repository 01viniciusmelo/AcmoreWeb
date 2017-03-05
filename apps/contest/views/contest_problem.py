from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from apps.contest.models import Contest
from apps.contest.models import ContestProblem
from apps.problem.models.OJproblem import Problem as OJproblem
from apps.status.models.Solution import Solution
from apps.source.models import SourceCode
from apps.source.models import OjSourceCode

import json


def problem_content(request):
    contest_id = request.GET.get('contest', 0)

    try:
        contest = Contest.objects.get(contest_id=contest_id)
    except Contest.DoesNotExist:
        context = dict(
            status=400,
            message='no such contest'
        )
        return HttpResponse(json.dumps(context), content_type="application/json")

    if timezone.now() < contest.start_time:
        context = dict(
            status=400,
            message='contest not start.'
        )
        return HttpResponse(json.dumps(context), content_type="application/json")


    judge_name = request.GET.get('name', 'oj')
    problem_order_number = request.GET.get('problem', '')
    type = request.GET.get('type', 'json')

    if problem_order_number == '':
        return HttpResponse('no such problem')

    if judge_name == 'oj':
        if 'A' <= problem_order_number <= 'Z':
            contest_problem_num = ord(problem_order_number) - ord('A')
        elif 'a' <= problem_order_number <= 'z':
            contest_problem_num = ord(problem_order_number) - ord('a') + 26
        else:
            return HttpResponse('no such problem')

        contest_problem_info = ContestProblem.objects.values('problem_id','title') \
            .filter(num=contest_problem_num).filter(contest_id=contest_id).get()
        real_problem_id = contest_problem_info['problem_id']

        _problem = OJproblem.objects.values('title','description','input','output',
                                            'sample_input','sample_output','spj','hint','time_limit','memory_limit'
                                            ).get(problem_id=real_problem_id)

        problem = dict()
        problem['a'] = list() #with attributes, t:1 show value, 2 not show value and strong attr
        problem['d'] = list() #in description, t:1 text, 2 html
        problem['type'] = 'text'

        problem['a'].append(dict(
            k='Time Limit',
            v=str(_problem['time_limit']) + ' s',
            t='1'
        ))
        problem['a'].append(dict(
            k='Memory limit',
            v=str(_problem['memory_limit']).encode('utf-8') + 'MB',
            t='1'
        ))
        if _problem['spj'] == 1:
            problem['a'].append(dict(
                k='Special Judge',
                t='2'
            ))

        problem['title'] = contest_problem_info['title']

        problem['d'].append(dict(
            k='Description',
            v=_problem['description'],
            t='2'
        ))
        problem['d'].append(dict(
            k='Input',
            v=_problem['input'],
            t='2'
        ))
        problem['d'].append(dict(
            k='Output',
            v=_problem['output'],
            t='2'
        ))
        problem['d'].append(dict(
            k='Sample input',
            v=_problem['sample_input'],
            t='1'
        ))
        problem['d'].append(dict(
            k='Sample output',
            v=_problem['sample_output'],
            t='1'
        ))
        problem['d'].append(dict(
            k='Hint',
            v=_problem['hint'],
            t='2'
        ))

        context = dict(
            problem=problem,
            status=200
        )
        return HttpResponse(json.dumps(context), content_type="application/json")

@login_required
def submit_problem(request, contest_id):
    contest = Contest.objects.get(contest_id=contest_id)

    if timezone.now() > contest.end_time:
        return HttpResponseRedirect(reverse('one_contest', args=[contest_id, ]))

    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip_address = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip_address = request.META['REMOTE_ADDR']

    try:
        problem_order_number = request.POST.get('problem', 'A')
        if 'A' <= problem_order_number <= 'Z':
            problem_order_number = ord(problem_order_number) - ord('A')
        elif 'a' <= problem_order_number <= 'z':
            problem_order_number = ord(problem_order_number) - ord('a')
        else:
            return HttpResponse('some error happened')

        contest_problem = ContestProblem.objects.values('problem_id', 'num') \
            .filter(contest_id=contest_id).filter(num=problem_order_number).get()

        lang = int(request.POST.get('language', ''))
    except ValueError:
        return HttpResponse('some error happened')

    source_code = request.POST.get('source', '')

    problem_id = contest_problem['problem_id']
    pnum = contest_problem['num']

    solution = Solution(
        problem_id=problem_id,
        user_id=request.user.username,
        language=lang,
        ip=ip_address,
        code_length=int(len(source_code.encode("utf-8"))),
        in_date=timezone.now(),
        result=0,
        time=0,
        memory=0,
        valid=1,
        num=pnum,
        pass_rate=0,
        lint_error=0,
        judger='waiting',
        contest_id=contest_id
    )

    solution.save()

    ss = SourceCode(
        solution_id=solution.solution_id,
        source=source_code
    )
    ss.save()

    sss = OjSourceCode(
        solution_id=solution.solution_id,
        source=source_code
    )
    sss.save()

    return HttpResponseRedirect(reverse('one_contest', args=[contest_id, ]) + '#status')
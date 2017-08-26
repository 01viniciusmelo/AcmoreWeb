from django.utils import timezone
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from apps.contest.models import Contest
from apps.contest.models import ContestProblem
from apps.problem.models.Problem import Problem
from apps.status.models.Solution import Solution
from apps.source.models import SourceCode
from apps.source.models import OjSourceCode
from apps.models import JudgeLanguage

from const import language_name, support_language

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

        print real_problem_id

        problem = Problem.objects.values('title','description','input','output','judge_name',
                                            'sample_input','sample_output','spj','hint','time_limit','memory_limit'
                                            ).get(rec_id=real_problem_id)

        response_problem = dict()
        response_problem['a'] = list() #with attributes, t:1 show value, 2 not show value and strong attr
        response_problem['d'] = list() #in description, t:1 text, 2 html
        response_problem['type'] = 'text'

        response_problem['a'].append(dict(
            k='Time Limit',
            v=problem['time_limit'] + 's' if problem['judge_name'] == 'LOCAL' else problem['time_limit'],
            t='1'
        ))
        response_problem['a'].append(dict(
            k='Memory limit',
            v=problem['memory_limit'] + 'MB' if problem['judge_name'] == 'LOCAL' else problem['memory_limit'],
            t='1'
        ))
        if int(problem['spj']) == 1:
            response_problem['a'].append(dict(
                k='Special Judge',
                t='2'
            ))

        response_problem['title'] = contest_problem_info['title']

        response_problem['d'].append(dict(
            k='Description',
            v=problem['description'],
            t='2'
        ))
        response_problem['d'].append(dict(
            k='Input',
            v=problem['input'],
            t='2'
        ))
        response_problem['d'].append(dict(
            k='Output',
            v=problem['output'],
            t='2'
        ))
        response_problem['d'].append(dict(
            k='Sample input',
            v=problem['sample_input'],
            t='1'
        ))
        response_problem['d'].append(dict(
            k='Sample output',
            v=problem['sample_output'],
            t='1'
        ))
        response_problem['d'].append(dict(
            k='Hint',
            v=problem['hint'],
            t='2'
        ))

        if problem['judge_name'] == 'LOCAL':
            permit_languages = support_language
        else:
            permit_languages = [[i.language_id, i.language_name] for i in JudgeLanguage.objects.filter(judge_name=problem['judge_name'])]

        response_problem['l'] = permit_languages

        context = dict(
            problem=response_problem,
            status=200
        )
        return JsonResponse(context)

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
        lang = int(request.POST.get('language', ''))
        problem_order_number = request.POST.get('problem', '')
        if 'A' <= problem_order_number <= 'Z':
            problem_order_number = ord(problem_order_number) - ord('A')
        elif 'a' <= problem_order_number <= 'z':
            problem_order_number = ord(problem_order_number) - ord('a')
        else:
            return HttpResponse('some error happened')

        contest_problem = ContestProblem.objects.values('problem_id', 'num') \
            .filter(contest_id=contest_id).filter(num=problem_order_number).get()

        problem = Problem.objects.get(rec_id=contest_problem['problem_id'])
    except:
        return HttpResponse('some error happened')

    source_code = request.POST.get('source', '')

    if problem.judge_name == 'LOCAL':
        judge_language_name = language_name[lang]
    else:
        judge_language_name = JudgeLanguage.objects.filter(judge_name=problem.judge_name).get(language_id=lang).language_name

    solution = Solution(
        problem_id=problem.problem_id,
        problem_rec_id=problem.rec_id,
        user_id=request.user.username,
        language=lang,
        language_name=judge_language_name,
        ip=ip_address,
        code_length=int(len(source_code.encode("utf-8"))),
        in_date=timezone.now(),
        result=0,
        time=0,
        memory=0,
        valid=1,
        num=contest_problem['num'],
        pass_rate=0,
        lint_error=0,
        judger='waiting',
        contest_id=contest_id,
        judge_type=0 if problem.judge_name == 'LOCAL' else 1,
        judge_name=problem.judge_name
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


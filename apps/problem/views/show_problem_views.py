from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from django.http import JsonResponse
from django.shortcuts import render

from apps.problem.models.Problem import Problem
from apps.status.models.Solution import Solution
from apps.models import JudgeLanguage

from const import support_language, vjudge_problem_url

import urllib
import time
import json


def one_problem(request, judge_name, problem_id):
    start_time = time.time()
    try:
        problem = cache.get_or_set('problem_oj' + str(problem_id), Problem.objects.filter(judge_name=judge_name).get(problem_id=problem_id), 3)
    except ObjectDoesNotExist:
        return render(request, 'no-problem.html')

    if problem.source != '':
        pass
    else:
        problem.source = 'None'

    attr = dict()
    if problem.attrs != '' and problem.attrs is not None:
        attr = json.loads(problem.attrs)

    submit_alert = 'Judge services will be provided by %s oj.\
                    Make sure your code length is longer than 50 and not exceed 65536 Bytes.' % problem.judge_name
    if judge_name == 'LOCAL':
        language = support_language
    else:
        language = [[item.language_id, item.language_name] for item in JudgeLanguage.objects
                        .filter(judge_name=judge_name).filter(enabled=1).order_by('language_id').all()]

    v_problem_url = vjudge_problem_url[problem.judge_name] + problem.problem_id if problem.judge_name != 'LOCAL' else ''

    context = dict(
        problem=problem,
        used_time=round((time.time() - start_time) * 1000, 2),
        attr=attr,
        support_language=language,
        submit_alert=submit_alert,
        v_problem_url=v_problem_url
    )
    return render(request, 'one-problem.html', context=context)

def problem_list(request):
    return render(request, 'problem-list.html')

def problem_list_data(request):
    page_params = '#'

    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 20))
        source  = request.GET.get('source', '')
        title  = request.GET.get('title', '')
        problem_id  = request.GET.get('problem', '')
        judge_name  = request.GET.get('judge_name', '')
    except ValueError:
        return render(request, '404.html', status=404)

    limit = 100 if limit > 100 else limit

    filter = dict(
        source=source,
        title=title,
        problem=problem_id
    )

    problems = Problem.objects.filter(defunct='N')

    if source != '':
        problems = problems.filter(source__contains=source)
        page_params = page_params + '/source-' + urllib.quote(source.encode('utf-8'))

    if title != '':
        problems = problems.filter(title__contains=title)
        page_params = page_params + '/title-' + urllib.quote(title.encode('utf-8'))

    if problem_id != '':
        problems = problems.filter(problem_id__contains=problem_id)
        page_params = page_params + '/problem-' + urllib.quote(problem_id.encode('utf-8'))

    if judge_name != '' and judge_name != 'ALL':
        problems = problems.filter(judge_name=judge_name)
        page_params = page_params + '/judge_name-' + judge_name

    problems = problems.order_by('rec_id')

    problem_number = problems.count()

    problems = problems[offset*limit:(offset+1)*limit]

    s_submitted = list()
    s_accepted = list()

    if request.user.is_authenticated():
        problem_id_list = [i['rec_id'] for i in problems.values('rec_id')]

        user_id = request.user.username
        solution_submitted = Solution.objects.values('problem_rec_id')\
            .filter(problem_rec_id__in=problem_id_list).filter(user_id=user_id)

        if judge_name != '' and judge_name != 'ALL':
            solution_submitted = solution_submitted.filter(judge_name=judge_name)

        s_submitted = [i['problem_rec_id'] for i in solution_submitted.values('problem_rec_id').distinct()]
        s_accepted = [i['problem_rec_id'] for i in solution_submitted.filter(result=4).values('problem_rec_id').distinct()]

    context = dict(
        problems=list(problems.values('rec_id', 'problem_id', 'title', 'source', 'in_date', 'accepted',
                                      'submit', 'judge_name'))
    )

    for problem in context['problems']:
        if int(problem['rec_id']) in s_submitted:
            if int(problem['rec_id']) in s_accepted:
                problem['user_status'] = 2
            else:
                problem['user_status'] = 1
        else:
            problem['user_status'] = 0
        del(problem['rec_id'])

        problem['rate'] = 0 if int(problem['submit']) == 0 else \
            int(problem['accepted'])*100/int(problem['submit'])


    page_params = page_params + '/limit-' + str(limit) + '/offset-' + str(offset)

    if offset == 0:
        previous = ['Previous', 'disabled', 0]
    else:
        previous = ['Previous', 'default', offset - 1]

    pages = [previous,]
    half_pagination_number = 5

    if problem_number / limit + 1 < half_pagination_number * 2 or offset <= half_pagination_number:
        if problem_number / limit + 1 < half_pagination_number * 2:
            tail = problem_number / limit + 1
        else:
            tail = half_pagination_number * 2

        if problem_number / limit + 1 > tail:
            for i in range(0, tail - 2):
                class_ = 'active' if offset == i else 'default'
                pages.append([i + 1, class_, i])

            pages.append(['...', 'disabled', 0])
            pages.append([problem_number / limit + 1, 'default', problem_number / limit])
        else:
            for i in range(0, tail):
                class_ = 'active' if offset == i else 'default'
                pages.append([i + 1, class_, i])
    else:
        pages.append([1, 'default', 0])
        pages.append(['...', 'disabled', 0])

        if problem_number / limit + 1 - half_pagination_number > offset:
            for i in range(offset - (half_pagination_number - 2), offset):
                pages.append([i + 1, 'default', i])

            pages.append([offset + 1, 'active', offset])
            for i in range(offset + 1, offset + (half_pagination_number - 2)):
                pages.append([i + 1, 'default', i])

            pages.append(['...', 'disabled', 0])
            pages.append([problem_number / limit + 1, 'default', problem_number / limit])
        else:
            remainder_page_number = problem_number / limit - offset
            for i in range(offset - (half_pagination_number + 2 - remainder_page_number), offset):
                pages.append([i + 1, 'default', i])

            pages.append([offset + 1, 'active', offset])

            for i in range(offset + 1, offset + 1 + remainder_page_number):
                pages.append([i + 1, 'default', i])

    if (offset + 1) * limit < problem_number:
        next = ['Next', 'default', offset + 1]
    else:
        next = ['Next', 'disabled', offset + 1]

    pages.append(next)

    context['page_params'] = page_params
    context['pages'] = pages

    return JsonResponse(context)

from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.cache import cache

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from apps.problem.models.OJproblem import Problem as OJproblem
from apps.status.models.Solution import Solution

from const import support_language

import math
import time


def one_problem(request, problem_id):
    start_time = time.time()
    try:
        problem = cache.get_or_set('problem_oj' + str(problem_id), OJproblem.objects.get(problem_id=problem_id), 60)
    except ObjectDoesNotExist:
        return render(request, 'no-problem.html')

    context = dict(
        problem=problem,
        used_time=round((time.time() - start_time) * 1000, 2),
        support_language=support_language,
    )

    return render(request, 'one-problem.html', context=context)


def problem_list(request):
    try:
        offset = int(request.GET.get('offset', 1000))
        limit = int(request.GET.get('limit', 100))
    except ValueError:
        return render(request, '404.html', status=404)

    if limit > 100:
        limit = 100

    problems = OJproblem.objects \
        .filter(defunct='N').filter(problem_id__gte=offset).filter(problem_id__lt=offset + limit)\
        .order_by('problem_id')

    s_submitted = list()
    s_accepted = list()

    if request.user.is_authenticated():
        user_id = request.user.username
        solution_submitted = Solution.objects.values('problem_id').filter(problem_id__gte=offset).filter(problem_id__lt=offset + limit)\
                            .filter(user_id=user_id)
        solution_submitted.query.group_by = ['problem_id']
        solution_accepted = solution_submitted.filter(result=4)

        s_submitted = map(lambda x:x['problem_id'], solution_submitted)
        s_accepted = map(lambda x:x['problem_id'], solution_accepted)


    for problem in problems:
        if problem.problem_id in s_submitted:
            if problem.problem_id in s_accepted:
                problem.user_status = 2
            else:
                problem.user_status = 1
        else:
            problem.user_status = 0

        problem.rate = 0 if int(problem.submit) == 0 else int(problem.accepted)*100/int(problem.submit)

    context = dict(
        problems=problems
    )

    last_problem_id = OJproblem.objects.all().order_by('-problem_id')[0].problem_id

    page_total = last_problem_id / limit
    pages = []

    for page_number in range(1000/limit, page_total+1):
        page = dict()
        page['name'] = '~P'+str(page_number*limit)
        page['url'] = reverse('oj_problem_list')+'?offset='+str(page_number*limit)+'&limit='+str(limit)
        if page_number*limit == offset:
            page['status'] = 'active'
        pages.append(page)

    context['pages'] = pages
    context['page_action'] = reverse('oj_problem_list')
    context['this_offset'] = offset
    context['this_limit'] = limit
    context['len'] = len(problems)
    context['limit_url'] = reverse('oj_problem_list')

    return render(request, 'problem-list.html', context=context)


def problem_list_by_search(request):
    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 100))

        search_type = request.GET.get('type')
        content = request.GET.get('content')
    except ValueError:
        return render(request, '404.html', status=404)

    if limit > 100:
        limit = 100

    problems = OJproblem.objects.filter(defunct='N').order_by('problem_id')

    if search_type == 'author':
        problems = problems.filter(source__contains=content.encode('utf-8'))
    elif search_type == 'keyword':
        problems = problems.filter(Q(title__contains=content) | Q(description__contains=content))
    else:
        return HttpResponse('parameter error')

    problem_set_total = problems.count()
    problems = problems[offset * limit:(offset + 1) * limit]
    try:
        left_id = problems[0].problem_id
        right_id = problems[problems.count()-1].problem_id
    except IndexError:
        left_id = right_id = 0

    s_submitted = list()
    s_accepted = list()

    if request.user.is_authenticated():
        user_id = request.user.username
        solution_submitted = Solution.objects.values('problem_id').filter(problem_id__gte=left_id)\
            .filter(problem_id__lt=right_id).filter(user_id=user_id)
        solution_submitted.query.group_by = ['problem_id']
        solution_accepted = solution_submitted.filter(result=4)

        s_submitted = map(lambda x: x['problem_id'], solution_submitted)
        s_accepted = map(lambda x: x['problem_id'], solution_accepted)

    for problem in problems:
        if problem.problem_id in s_submitted:
            if problem.problem_id in s_accepted:
                problem.user_status = 2
            else:
                problem.user_status = 1
        else:
            problem.user_status = 0
        problem.rate = 0 if int(problem.submit) == 0 else int(problem.accepted)*100/int(problem.submit)

    pages = []
    for page_number in range(0, int(math.ceil(float(problem_set_total) / limit))):
        page = dict()
        page['name'] = 'Page '+str(page_number)
        page['url'] = reverse('oj_problem_list_by_search') \
                      +'?content='+content+'&type='+search_type+'&offset='\
                      +str(page_number)+'&limit='+str(limit)
        pages.append(page)

    context = dict()
    context['problems'] = problems
    context['pages'] = pages
    context['this_offset'] = 0
    context['this_limit'] = limit
    context['len'] = len(problems)
    context['search'] = dict(
        type=search_type,
        content=content,
    )
    context['limit_url'] = reverse('oj_problem_list_by_search')

    return render(request, 'problem-list.html', context=context)

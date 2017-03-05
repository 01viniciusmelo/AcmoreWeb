from django.http import HttpResponse

from django.core.exceptions import *
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.shortcuts import render

from apps.status.models.Solution import RunTimeInfo
from apps.status.models.Solution import CompileInfo
from apps.status.models.Solution import Solution
from apps.contest.models import Contest
from const import language_name, support_language, judger_name, judge_result, judge_result_type, index_order

import time
import calendar
import json


def status_list(request):
    context = dict()
    limit = 20
    page_param = ''

    content_type = request.GET.get('content', 'html')
    order_field = request.GET.get('order', 'in_date')

    if order_field == 'memory':
        page_param += '&order=memory'
        solutions = Solution.objects.filter(~Q(problem_id=0)).order_by('memory', 'time')
    elif order_field == 'time':
        page_param += '&order=time'
        solutions = Solution.objects.filter(~Q(problem_id=0)).order_by('time', 'memory')
    else:
        solutions = Solution.objects.filter(~Q(problem_id=0)).order_by('-solution_id')

    page_number = 0

    offset = int(request.GET.get('offset', 0))
    problem = request.GET.get('problem', '').encode('utf-8')
    user_id = request.GET.get('user_id', '').encode('utf-8')
    language = request.GET.get('language', '').encode('utf-8')
    result = request.GET.get('result', '').encode('utf-8')

    if problem != '':
        page_param = page_param + "&problem=" + str(problem)
        context['problem'] = problem
        try:
            problem = int(problem)
        except ValueError:
            problem = 0
        solutions = solutions.filter(problem_id=problem)
    if user_id != '':
        page_param = page_param + "&user_id=" + str(user_id)
        context['user_id'] = user_id
        solutions = solutions.filter(user_id=user_id)
    if language != '':
        page_param = page_param + "&language=" + language
        try:
            language = int(language)
        except ValueError:
            language = -1
        context['language'] = int(language)
        solutions = solutions.filter(language=language)
    if result != '':
        page_param = page_param + "&result=" + result
        try:
            result = int(result)
        except ValueError:
            result = -1
        context['result'] = judge_result[int(result)] if int(result) < 100  else 'Others'
        solutions = solutions.filter(result=result) if int(result) < 100  else solutions.filter(result__lt=4)

    start_time = time.time()

    if request.GET.get('type', 'normal') != 'normal':
        print ('sss')

    if content_type == 'json':
        page_number = cache.get_or_set('solutions_count_' +page_param, solutions.count(), 3)

    solutions = solutions[offset * limit:(offset + 1) * limit]

    used_time = round((time.time() - start_time)*1000, 2)

    for solution in solutions:
        solution.language = language_name[solution.language]
        solution.judger = judger_name[solution.judger]
        solution.result_text = judge_result[solution.result]
        solution.moreinfo = 10 <= solution.result <= 11
        solution.result_type = judge_result_type[solution.result]

    context['used_time'] = used_time
    context['page_param'] = page_param
    context['offset'] = offset
    context['limit'] = limit

    if content_type == 'json':
        context['page_number'] = page_number
        context['solutions'] = list(solutions.values('solution_id', 'problem_id', 'user_id', 'time', 'memory', 'in_date',
                                     'result', 'language', 'code_length'))

        return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")
    else:
        context['support_language'] = support_language
        context['judge_result'] = judge_result
        for solution in solutions:
            solution.in_date_timestamp = calendar.timegm(solution.in_date.timetuple())*1000
        context['solutions'] = solutions
        return render(request, 'status-list.html', context=context)


@login_required(redirect_field_name='from_url')
def runtime_info(request, run_id):
    result = int(request.GET['result'])

    context = dict(
        run_id=run_id,
        title=''
    )

    try:
        if result == 10:
            run_info = RunTimeInfo.objects.get(solution_id=run_id)
            context['title'] = 'Runtime information.'
        elif result == 11:
            run_info = CompileInfo.objects.get(solution_id=run_id)
            context['title'] = 'Compile information.'
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        return HttpResponse('No Such Information', status=404)

    context['run_info'] = run_info

    return render(request, 'runtime-info.html', context=context)



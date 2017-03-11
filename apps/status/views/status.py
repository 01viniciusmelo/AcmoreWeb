from django.http import HttpResponse
from django.http import JsonResponse

from django.core.exceptions import *
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from django.shortcuts import render

from apps.status.models.Solution import RunTimeInfo
from apps.status.models.Solution import CompileInfo
from apps.status.models.Solution import Solution
from const import language_name, support_language, judger_name, judge_result, judge_result_type, vjudge_problem_url

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
    judge_name = request.GET.get('judge_name', 'ALL').encode('utf-8')

    page_param = page_param + "&judge_name=" + judge_name
    if judge_name != 'ALL':
        solutions = solutions.filter(judge_name=judge_name)

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

    if content_type == 'json':
        page_number = cache.get_or_set('solutions_count_'+page_param.replace(' ', ''), solutions.count(), 3)

    solutions = solutions[offset * limit:(offset + 1) * limit]

    for solution in solutions:
        solution.language = language_name[solution.language]
        solution.judger = judger_name[solution.judger]
        if solution.judge_type == 0:
            solution.moreinfo = 10 <= solution.result <= 11
        else:
            if solution.judge_name == 'HDU':
                solution.moreinfo = 11 == solution.result
        solution.result_type = judge_result_type[solution.result]

    context['page_param'] = page_param
    context['offset'] = offset
    context['limit'] = limit

    if content_type == 'json':
        context['page_number'] = page_number

        context['solutions'] = list(solutions.values('solution_id', 'problem_id', 'user_id', 'time', 'memory', 'in_date',
                                                 'result', 'result_name', 'language_name', 'code_length'))
        for item in context['solutions']:
            if item['result_name'] == '' or item['result_name'] == None:
                item['result_name'] = judge_result[item['result']]

        return JsonResponse(context)
    else:
        context['support_language'] = support_language
        context['judge_result'] = judge_result

        for item in solutions:
            if item.result_name == '' or item.result_name is None:
                item.result_name = judge_result[item.result]
            if item.judge_type > 0:
                item.vjudge_problem_url = vjudge_problem_url[item.judge_name] + str(item.problem_id)

        context['solutions'] = solutions

        return render(request, 'status-list.html', context=context)


@login_required(redirect_field_name='from_url')
def runtime_info(request, run_id):
    context = dict(
        run_id=run_id,
        title=''
    )

    try:
        solution = Solution.objects.values('result', 'result_name', 'language_name').get(solution_id=run_id)

        if solution['result'] == 10:
            context['title'] = 'Runtime information.'
            run_info = RunTimeInfo.objects.get(solution_id=run_id)
        elif solution['result'] == 11:
            context['title'] = 'Compile information.'
            run_info = CompileInfo.objects.get(solution_id=run_id)
        elif request.user.is_superuser:
            run_info = RunTimeInfo.objects.get(solution_id=run_id)
        else:
            raise ObjectDoesNotExist

        if solution['result_name'] == '':
            solution['result_name'] = judge_result[solution['result']]

    except ObjectDoesNotExist:
        return HttpResponse('No Such Information')
    else:
        context['run_info'] = run_info
        context['solution'] = solution

        return render(request, 'runtime-info.html', context=context)



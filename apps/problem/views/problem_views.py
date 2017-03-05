from django.utils import timezone
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.status.models.Solution import Solution
from apps.source.models import SourceCode
from apps.source.models import OjSourceCode

import json


def only_problem(request):
    request_type = request.GET.get('type')
    if request_type == 'problem':
        name = request.GET.get('name')
        try:
            problem_id = int(request.GET.get('problem_id'))
        except ValueError:
            return render(request, '404.html', status=404)

        if name == 'oj':
            return HttpResponseRedirect(reverse('oj_one_problem', args=[problem_id, ]))


@login_required
def submit_problem(request, judge_name, problem_id):
    if judge_name == 'online':
        return submit_online_problem(request, problem_id)


def submit_online_problem(request, problem_id):
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip_address = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip_address = request.META['REMOTE_ADDR']

    try:
        problem_id = int(problem_id)
        lang = int(request.POST.get('language', ''))
    except ValueError:
        return HttpResponse('some error happened')

    source_code = request.POST.get('source', '')

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
        num=-1,
        pass_rate=0,
        lint_error=0,
        judger='waiting'
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

    return HttpResponseRedirect(reverse('oj_one_problem', args=[problem_id, ])+'#submissions')









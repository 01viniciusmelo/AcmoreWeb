from django.utils import timezone
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.status.models.Solution import Solution
from apps.source.models import SourceCode
from apps.source.models import OjSourceCode
from apps.problem.models.Problem import Problem
from apps.models import JudgeLanguage

from const import language_name, source_code_length_limit


@login_required
def submit_problem(request, judge_name, problem_id):
    source_code = request.POST.get('source', '')

    if source_code_length_limit[judge_name][0] < len(source_code) < source_code_length_limit[judge_name][1]:
        pass
    else:
        return render(request, 'error.html', context=dict(error_msg='Source code size check failed.'))

    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip_address = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip_address = request.META['REMOTE_ADDR']

    try:
        problem_id = int(problem_id)
        lang = int(request.POST.get('language', ''))
    except ValueError:
        return HttpResponse('some error happened')

    if judge_name == 'LOCAL':
        judge_language_name = language_name[lang]
    else:
        judge_language_name = JudgeLanguage.objects.filter(judge_name=judge_name).get(language_id=lang).language_name

    try:
        problem = Problem.objects.filter(judge_name=judge_name).get(problem_id=problem_id)
    except Problem.DoesNotExist:
        return HttpResponse('No such problem')

    solution = Solution(
        problem_rec_id=problem.rec_id,
        problem_id=problem.problem_id,
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
        num=-1,
        pass_rate=0,
        lint_error=0,
        judger='waiting',
        judge_type=0 if judge_name=='LOCAL' else 1,
        judge_name=judge_name
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

    ac_submit_number = Solution.objects.filter(problem_id=problem_id).filter(judge_name=judge_name).filter(result=4).count()
    all_submit_number = Solution.objects.filter(problem_id=problem_id).filter(judge_name=judge_name).count()

    problem = Problem.objects.filter(problem_id=problem_id).filter(judge_name=judge_name).get()

    problem.accepted = ac_submit_number
    problem.submit = all_submit_number

    problem.save()

    return HttpResponseRedirect(reverse('one_problem', args=[judge_name, problem_id, ])+'#submissions')


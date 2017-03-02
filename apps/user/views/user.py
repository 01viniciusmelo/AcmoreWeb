from django.http import HttpResponse
from django.db.models import Count
from django.db.models import Q
from django.shortcuts import render
from apps.status.models.Solution import Solution
from apps.user.models.OldUser import OldUser
from const import language_name, language_enable, judge_result_color, judge_result

import math


def user_info(request, username):
    try:
        user = OldUser.objects.get(user_id=username)

    except OldUser.DoesNotExist:
        return HttpResponse('User not found.')

    total_solved_number = Solution.objects.filter(result=4).filter(user_id=username).values('problem_id').distinct().count()
    total_submit_number = Solution.objects.filter(problem_id__gt=0).filter(user_id=username).count()

    user.solved = total_solved_number
    user.submit = total_submit_number
    user.save()

    total_result = Solution.objects.filter(user_id=username).filter(result__gte=4).filter(problem_id__gt=0)\
                    .values('result').annotate(count=Count(1)).order_by('result')

    total_wrong_number = 0
    total_wrong = list()
    total_others_number = 0
    total_others = list()
    total_ac_number = 0
    for result in total_result:
        result['color'] = judge_result_color[result['result']]
        result['name'] = judge_result[result['result']]
        if result['result'] == 4:
            total_ac_number += result['count']
        elif result['result'] == 6 or result['result'] == 10 or result['result'] == 11:
            total_wrong_number += result['count']
            total_wrong.append(result)
        else:
            total_others_number += result['count']
            total_others.append(result)

    solutions_ac = Solution.objects.filter(user_id=username).filter(~Q(problem_id=0)).filter(result=4)\
        .order_by('problem_id').values('problem_id').distinct()
    solutions_wa = Solution.objects.filter(user_id=username).filter(~Q(problem_id=0)).filter(~Q(result=4)).filter(~Q(problem_id__in=solutions_ac))\
        .order_by('problem_id').values('problem_id').distinct()

    context = dict(
        u=user,
        solutions_ac=solutions_ac,
        solutions_wa=solutions_wa,
        total_solved_number=total_solved_number,
        total_ac_number=total_ac_number,
        total_wrong_number=total_wrong_number,
        total_wrong=total_wrong,
        total_others_number=total_others_number,
        total_others=total_others,
        total_submit_number=total_submit_number,
    )
    return render(request, 'one-user.html', context=context)


def user_list(request):
    query_param = ''

    try:
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 50))
        query_param = query_param + '&limit=' + str(limit)
    except ValueError:
        return HttpResponse('404', status=404)

    if limit > 50:
        limit = 50

    start_record = offset * limit

    content = request.GET.get('content', False)

    if content:
        query_param = query_param + '&content=' + content
        users = OldUser.objects.filter(user_id__contains=content).order_by('-solved', 'submit')
    else:
        users = OldUser.objects.order_by('-solved', 'submit')

    user_number = users.count()

    users = users[start_record: start_record + limit]
    page_number = int(math.ceil(user_number / limit))

    context = dict(
        users=users,
        offset=offset,
        page_number=range(0, page_number + 1),
        has_next_page=(start_record + limit) < user_number,
        query_param=query_param,
        content=content if content else ''
    )
    return render(request, 'user-list.html', context=context)



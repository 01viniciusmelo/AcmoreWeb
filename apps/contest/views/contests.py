from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.serializers.json import DjangoJSONEncoder

from apps.contest.models import Contest
from apps.contest.models import ContestProblem
from apps.status.models.Solution import Solution
from apps.account.models import Privilege

from const import language_name, support_language, judger_name, judge_result, judge_result_type, index_order

import json
import time


def contest_list(request):
    contests = Contest.objects.raw("select * from contest \
                                   left join \
                                   (select * from privilege where rightstr like 'm%%') p \
                                   on concat('m',contest_id)=rightstr \
                                   WHERE contest.defunct = 'N' order by contest_id desc;")
    _contests = list()
    now_time = timezone.now()
    for contest in contests:
        temp = dict()
        temp['duration'] = contest.end_time - contest.start_time

        if contest.private == 0:
            temp['permissions'] = 'Public'
        elif contest.private == 1:
            temp['permissions'] = 'Protected'
        elif contest.private == 2:
            temp['permissions'] = 'Private'
        else:
            temp['permissions'] = 'Other'

        if now_time < contest.start_time:
            temp['status'] = 0
        elif now_time < contest.end_time:
            temp['status'] = 1
        else:
            temp['status'] = 2
        _contests.append(temp)


    context = dict(
        contests=zip(contests, _contests)
    )

    return render(request, "contest-list.html",context=context)


def one_contest(request, contest_id):
    contest_status = 1
    protected_status = 0

    try:
        contest = cache.get_or_set('one_contest_'+str(contest_id), Contest.objects.get(contest_id=contest_id), 5)
    except Contest.DoesNotExist:
        return render(request, 'error.html', status=404)

    contest.start_timestamp = int(time.mktime(contest.start_time.timetuple()))
    contest.end_timestamp = int(time.mktime(contest.end_time.timetuple()))

    contest.now_timestamp = time.time()

    if timezone.now() < contest.start_time:
        context = dict(
            contest_status=2,#not start
            contest=contest,
        )
        return render(request, 'one-contest.html', context=context)

    if contest.private != 0:
        try:
            Privilege.objects.filter(user_id=request.user.username).filter(rightstr='c'+str(contest_id)).get()
        except Privilege.DoesNotExist:
            if contest.private == 2:
                contest_status = 3#private with password
                context = dict(
                    contest_status=contest_status,
                    contest=contest,
                )
                return render(request, 'one-contest.html', context=context)
            else:
                protected_status = 1 #protected with password not passed
        else:
            protected_status = 0 #protected with password already passed


    contest.total_time = contest.end_time - contest.start_time

    sql =   "SELECT title, pid, pnum,accepted,submit,has_ac,has_submit FROM "\
            "(SELECT `contest_problem`.`title` AS `title`,`problem`.`rec_id` AS `pid`,contest_problem.num AS pnum "\
            "    FROM `contest_problem`,`problem` WHERE `contest_problem`.`problem_id`=`problem`.`rec_id` "\
            "    AND `contest_problem`.`contest_id`=%s ORDER BY `contest_problem`.`num` "\
            ")AS t_problem "\
            "LEFT JOIN "\
            "    (SELECT problem_rec_id AS pid1,COUNT(DISTINCT(user_id)) AS accepted "\
            "FROM solution WHERE contest_id=%s AND result=4 GROUP BY pid1) AS p1 "\
            "ON t_problem.pid=p1.pid1 "\
            "LEFT JOIN "\
            "    (SELECT problem_rec_id AS pid2,COUNT(1) AS submit FROM solution WHERE contest_id=%s GROUP BY pid2) p2 "\
            "ON t_problem.pid=p2.pid2 "\
            "LEFT JOIN "\
            "    (SELECT problem_rec_id AS pid3,COUNT(1) AS has_ac from solution WHERE contest_id=%s AND solution.user_id=%s AND solution.result=4 GROUP BY pid3) p3 "\
            "ON t_problem.pid=p3.pid3 "\
            "LEFT JOIN "\
            "    (SELECT problem_rec_id AS pid4,COUNT(1) AS has_submit from solution WHERE contest_id=%s AND solution.user_id=%s GROUP BY pid4) p4 "\
            "ON t_problem.pid=p4.pid4 ORDER BY pnum;"

    cursor = connection.cursor()

    user_name = request.user.username

    cursor.execute(sql, (contest_id,contest_id,contest_id,contest_id,user_name,contest_id,user_name))
    raw = cursor.fetchall()

    order = map(lambda x:index_order[x[2]], raw)

    context = dict(
        contest=contest,
        problems=zip(order, raw),
        contest_status=contest_status,
        protected_status=protected_status,
        support_language=support_language,
        is_running = timezone.now() <= contest.end_time,
        show_rank=contest.show_rank,
        creator=cache.get_or_set('one_contest_creator_'+str(contest_id),
                                 Privilege.objects.values('user_id').get(rightstr='m'+str(contest_id))['user_id'], 60)
    )
    return render(request, 'one-contest.html', context=context)


def contest_rank(request):
    context = dict()

    contest_id = request.GET.get('contest', 0)

    if contest_id == 0:
        context['msg'] = 'No such contest.'
        return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")

    contest = Contest.objects.values('start_time','end_time').get(contest_id=contest_id)

    problem_number = ContestProblem.objects.filter(contest_id=contest_id).count()

    sql =   "SELECT "\
            "solutions.user_id, solutions.nick, solutions.result, solutions.num, solutions.in_date, first_solution.user_id AS fir "\
            "FROM ( "\
            "      SELECT users.user_id, users.nick, solution.result, solution.num, solution.in_date FROM "\
            "		(SELECT * FROM solution WHERE solution.contest_id=%s AND num>=0 AND problem_id>0) AS solution "\
            "      LEFT JOIN users ON users.user_id=solution.user_id "\
            ") AS solutions "\
            "LEFT JOIN ( "\
            "      SELECT num,user_id FROM "\
            "      (SELECT num,user_id FROM solution "\
            "      WHERE contest_id=%s AND result=4 ORDER BY solution_id ) AS contest "\
            "      GROUP BY num "\
            ") AS first_solution "\
            "ON first_solution.num=solutions.num AND first_solution.user_id = solutions.user_id AND solutions.result=4 "\
            "ORDER BY user_id,in_date;"

    cursor = connection.cursor()
    cursor.execute(sql, [contest_id, contest_id])

    users = list()
    user_name = ''
    user_number = -1

    for solution in cursor.fetchall():
        in_date = solution[4]
        if contest['end_time'].replace(tzinfo=None) < in_date or in_date < contest['start_time'].replace(tzinfo=None):
            continue

        this_problem = solution[3]
        this_result = solution[2]
        this_nick = solution[1]
        this_user = solution[0]

        if user_name == this_user:
            pass
        else:
            user_number += 1
            users.append(dict(
                user_name=this_user,
                user_nick=this_nick,
                used_time=0,
                solved=0,
                problem_wa_number=dict(),
                problem_ac_time=dict(),
                first_solved=dict()
            ))
            user_name = this_user

        used_time = time.mktime(in_date.timetuple()) \
                    - time.mktime(contest['start_time'].replace(tzinfo=None).timetuple())

        if this_result == 4:
            if 'problem_ac_time' in users[user_number]:
                if this_problem in users[user_number]['problem_ac_time'] and users[user_number]['problem_ac_time'] > 0:
                    continue

            if solution[5] is not None:
                users[user_number]['first_solved'][this_problem] = True

            users[user_number]['solved'] += 1
            users[user_number]['problem_ac_time'][this_problem] = used_time

            if this_problem not in users[user_number]['problem_wa_number']:
                users[user_number]['problem_wa_number'][this_problem] = 0

            users[user_number]['used_time'] += used_time + users[user_number]['problem_wa_number'][this_problem]*1200
        else:
            if this_problem not in users[user_number]['problem_wa_number']:
                users[user_number]['problem_wa_number'][this_problem] = 1
            else:
                users[user_number]['problem_wa_number'][this_problem] += 1


    context['problem_number'] = problem_number
    context['users'] = sorted(users, key=lambda user: (-user['solved'], user['used_time']))

    return JsonResponse(context)


@login_required
def check_contest_password(request):
    response = dict()
    try:
        contest_id = int(request.POST.get('contest_id', 0))
    except ValueError:
        response = dict(
            status=400,
            message='error'
        )
    else:
        contest = Contest.objects.get(contest_id=contest_id)

        password = request.POST.get('contestPassword', False)
        if contest.private != 0:
            if password and password == contest.password:
                privilege = Privilege(
                    user_id=request.user.username,
                    rightstr='c'+str(contest.contest_id),
                    defunct='N'
                )
                privilege.save()
                response = dict(
                    status=200,
                    message='update permission success'
                )
            else:
                response = dict(
                    status=304,
                    message='password error'
                )
        else:
            response = dict(
                status=204,
                message='password is unnecessary'
            )

    return JsonResponse(response)


def contest_status(request):
    context = dict()
    limit = 20
    page_param = ''
    offset = int(request.GET.get('offset', 0))
    only_user_code = request.GET.get('only', False)
    user_id = ''
    if only_user_code:
        try:
            only_user_code = int(only_user_code)
        except ValueError:
            return HttpResponse('haha')
        user_id = request.user.username if only_user_code == 1 else ''

    contest_id = request.GET.get('contest')
    contest = Contest.objects.get(contest_id=contest_id)

    solutions = Solution.objects.values('solution_id','num', 'user_id', 'time', 'memory', 'in_date', 'result',
                                        'language','language_name','result_name','judge_type','judge_name','code_length')\
                                        .filter(~Q(problem_id=0)).filter(contest_id=contest_id)\
                                        .filter(in_date__gte=contest.start_time).filter(in_date__lte=contest.end_time)\
                                        .order_by('-solution_id')

    page_param += '&contest=' + contest_id

    if user_id != '':
        page_param = page_param + "&user_id=" + str(user_id)
        context['user_id'] = user_id
        solutions = solutions.filter(user_id=user_id)

    page_number = cache.get_or_set('solutions_count_' +page_param, solutions.count(), 3)
    solutions = solutions[offset * limit:(offset + 1) * limit]


    def change_info_to_used(x):
        if x['user_id'] == request.user.username or request.user.is_superuser:
            x['source_code'] = reverse('only_source_by_run_id', args=[x['solution_id']])
        else:
            x['source_code'] = 0

        if x['judge_type'] == 0:
            if 10 <= x['result'] <= 11:
                x['runtime_info'] = reverse('runtime_info', args=[x['solution_id']]) + '?result=' + str(x['result'])
            else:
                x['runtime_info'] = 0
        elif x['judge_name'] == 'HDU':
            if x['result'] == 11:
                x['runtime_info'] = reverse('runtime_info', args=[x['solution_id']]) + '?result=' + str(x['result'])
            else:
                x['runtime_info'] = 0

        if x['result_name'] == '' or x['result_name'] == None:
            x['result_name'] = judge_result[x['result']]

        x['result_type'] = judge_result_type[x['result']]

        x['problem_id'] = index_order[x['num']]
        del x['num']
        del x['judge_type']
        del x['judge_name']
        del x['result']
        del x['solution_id']

    map(change_info_to_used, solutions)

    context['page_number'] = page_number
    context['solutions'] = list(solutions)
    context['offset'] = offset
    context['limit'] = limit

    return JsonResponse(context)


@login_required
def delete_one_contest(request, contest_id):
    response = dict(
        status=200,
        message='success',
        next_page=reverse('contest_list')
    )
    if str(contest_id) in request.META['HTTP_REFERER'] and request.POST.get('contest_id', -1) == contest_id:
        if request.user.is_superuser or request.user.username == Privilege.objects.values('user_id').get(rightstr='m'+str(contest_id))['user_id']:
            contest = Contest.objects.get(contest_id=contest_id)
            contest.defunct = 'Y'
            contest.save()
        else:
            response = dict(
                status=304,
                message='permission error',
                next_page=reverse('contest_list')
            )
    else:
        response = dict(
            status=403,
            message='error'
        )
    return JsonResponse(response)



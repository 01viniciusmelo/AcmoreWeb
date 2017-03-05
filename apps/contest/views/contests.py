from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import connection
from django.core.serializers.json import DjangoJSONEncoder

from apps.contest.models import Contest
from apps.contest.models import ContestProblem
from apps.status.models.Solution import Solution
from apps.source.models import SourceCode
from apps.source.models import OjSourceCode
from apps.problem.models.OJproblem import Problem as OJproblem
from apps.account.models import Privilege

from const import index_order, support_language
import json
import time


def contest_list(request):
    contests = Contest.objects.raw("select * from contest "
                                   "left join "
                                   "(select * from privilege where rightstr like 'm%%') p "
                                   "on concat('m',contest_id)=rightstr "
                                   "WHERE contest.defunct = 'N' order by contest_id desc;")
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
        contest = Contest.objects.get(contest_id=contest_id)
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
            p_str = 'c'+str(contest_id)
            Privilege.objects.filter(user_id=request.user.username).filter(rightstr=p_str).get()
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
            "( "\
            "    SELECT `contest_problem`.`title` AS `title`,`problem`.`problem_id` AS `pid`,contest_problem.num AS pnum "\
            "    FROM `contest_problem`,`problem` "\
            "    WHERE `contest_problem`.`problem_id`=`problem`.`problem_id` "\
            "    AND `contest_problem`.`contest_id`=%s ORDER BY `contest_problem`.`num` "\
            ")AS t_problem "\
            "LEFT JOIN "\
            "    (SELECT problem_id AS pid1,COUNT(1) AS accepted FROM solution "\
            "        WHERE contest_id=%s AND result=4 GROUP BY pid1) p1 "\
            "ON t_problem.pid=p1.pid1 "\
            "LEFT JOIN "\
            "    (SELECT problem_id AS pid2,COUNT(1) AS submit FROM solution "\
            "        WHERE contest_id=%s GROUP BY pid2) p2 "\
            "ON t_problem.pid=p2.pid2 "\
            "LEFT JOIN "\
            "    (SELECT problem_id AS pid3,COUNT(1) AS has_ac from solution "\
            "        WHERE contest_id=%s AND solution.user_id=%s AND solution.result=4 GROUP BY pid3) p3 "\
            "ON t_problem.pid=p3.pid3 "\
            "LEFT JOIN "\
            "    (SELECT problem_id AS pid4,COUNT(1) AS has_submit from solution "\
            "        WHERE contest_id=%s AND solution.user_id=%s GROUP BY pid4) p4 "\
            "ON t_problem.pid=p4.pid4;"


    cursor = connection.cursor()

    user_name = ''
    if request.user.is_authenticated():
        user_name = request.user.username

    cursor.execute(sql, [contest_id,contest_id,contest_id,contest_id,user_name,contest_id,user_name])
    raw = cursor.fetchall()
    # print((raw))

    order = map(lambda x:index_order[x[2]], raw)

    context = dict(
        contest=contest,
        problems=zip(order, raw),
        contest_status=contest_status,
        protected_status=protected_status,
        support_language=support_language,
        is_running = timezone.now() <= contest.end_time,
        show_rank=contest.show_rank,
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

    #print problem_number

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

    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder), content_type="application/json")


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

        contest_problem = ContestProblem.objects.values('problem_id', 'num')\
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

    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder), content_type="application/json")



















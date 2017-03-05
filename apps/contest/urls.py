from django.conf.urls import url
from apps.contest.views import contests
from apps.contest.views import contest_problem
from apps.contest.views import add_contest

urlpatterns = [
    url(r'^$', contests.contest_list, name='contest_list'),
    url(r'^(\d+)$', contests.one_contest, name='one_contest'),
    url(r'^rank/$', contests.contest_rank, name='contest_rank'),
    url(r'^status/$', contests.contest_status, name='contest_status'),
    url(r'^problem/$', contest_problem.problem_content, name='only_problem_by_id'),
    url(r'^submit/(\d+)$', contest_problem.submit_problem, name='submit_contest_problem'),

    url(r'^add/$', add_contest.create_contest, name='create_contest'),
    url(r'^add/problem/check$', add_contest.check_problem, name='check_contest_problem'),
    url(r'^add/submit$', add_contest.submit_contest, name='add_contest_submit'),
    url(r'^add/check-password$', contests.check_contest_password, name='check_contest_password'),

    url(r'^delete/(\d+)$', contests.delete_one_contest, name='delete_one_contest'),
]
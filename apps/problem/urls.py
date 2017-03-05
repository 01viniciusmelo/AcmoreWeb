from django.conf.urls import url
from views import oj_problem_views
from apps.problem.views import problem_views

urlpatterns = [
    url(r'^$', problem_views.only_problem, name='only_problem'),
    url(r'^submit/(?P<judge_name>[^/]+)/(?P<problem_id>[^/]+)$', problem_views.submit_problem, name='submit_problem'),

    url(r'^oj/(\d+)$', oj_problem_views.one_problem, name='oj_one_problem'),
    url(r'^oj/$', oj_problem_views.problem_list, name='oj_problem_list'),
    url(r'^oj/search$', oj_problem_views.problem_list_by_search, name='oj_problem_list_by_search'),

]

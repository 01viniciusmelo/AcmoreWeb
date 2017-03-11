from django.conf.urls import url
from views import show_problem_views
from apps.problem.views import problem_views

urlpatterns = [
    url(r'^submit/(?P<judge_name>[^/]+)/(?P<problem_id>[^/]+)$', problem_views.submit_problem, name='submit_problem'),

    url(r'^(?P<judge_name>[^/]+)/(?P<problem_id>\d+)$', show_problem_views.one_problem, name='one_problem'),
    url(r'^$', show_problem_views.problem_list, name='problem_list'),
    url(r'^api/list/$', show_problem_views.problem_list_data, name='problem_list_data'),

]

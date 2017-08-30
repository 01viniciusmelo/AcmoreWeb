"""judge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from apps.source import views as source_views
from apps.status.views import status
from apps.user.views import user
from apps.account import views as account
from apps.source.test import tests
import views as index_view


urlpatterns = [
    url(r'^$', index_view.index, name="index"),

    url(r'^problem/', include('apps.problem.urls'), name='problems'),

    url(r'^s/(?P<user_uuid>[^/]+)$', source_views.source_by_uuid, name='only_source_by_uuid'),
    url(r'^s/oj/(\d+)$', source_views.source_by_run_id, name='only_source_by_run_id'),
    url(r'^s/$', source_views.put_source, name='put_source'),

    url(r'^status/$', status.status_list, name='status_list'),

    url(r'^runtime/(\d+)$', status.runtime_info, name='runtime_info'),

    url(r'^user/(?P<username>[^/]+)$', user.user_info, name='one_user_info'),
    url(r'^user/$', user.user_list, name='user_list'),

    url(r'^test$', tests.test_run),
    url(r'^login$', account.login, name='account_login'),
    url(r'^register$', account.register, name='account_register'),
    url(r'^register/check', account.register_check, name='account_register_check'),
    url(r'^logout', account.logout, name='account_logout'),

    url(r'^account$', account.user_center, name='user_center'),
    url(r'^account/action/check-email$', account.check_email, name='user_check_email'),
    url(r'^account/action/information$', account.modify_information, name='user_modify_information'),

    url(r'^contest/', include('apps.contest.urls')),

    url(r'^thanks$', index_view.thanks, name='thanks'),
    url(r'^help$', index_view.help, name='help'),

    url(r'^article/', include('apps.article.urls')),

    url(r'^marquee-message$', index_view.marquee_message, name='marquee_message'),

]

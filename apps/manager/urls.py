from django.conf.urls import url
import views

urlpatterns = [
    url(r'^change-password/$', views.change_password, name='change_password'),
    url(r'^user-checker/$', views.check_user, name='check_user'),

]

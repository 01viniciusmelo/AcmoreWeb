from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.get_articles, name='get_articles'),
    url(r'^(\d+)$', views.one_article, name='one_article'),

]

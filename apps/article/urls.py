from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$', views.get_articles, name='article_list'),
    url(r'^(\d+)$', views.one_article, name='one_article'),

    url(r'image-receiver$', views.image_receiver, name='image_receiver'),

    url(r'post-receiver$', views.post_receiver, name='post_receiver'),


]

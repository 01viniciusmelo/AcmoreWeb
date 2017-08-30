from django.shortcuts import render
from django.db.models import Count
from apps.article.models import Article, Reply
from apps.account.models import User
from django.http.response import JsonResponse, HttpResponse
from const import gravatar_cdn
import collections

import hashlib


def get_articles(request):
    offset = request.GET.get("offset", 0)
    articles = Article.objects.all().annotate(comment_count=Count('reply')) \
    .values('tid','content','title', 'author__email', 'author__username', 'updated_at', 'comment_count')\
    .order_by("-updated_at")[:20]

    print articles.query

    for i in articles:
        i['gravatar'] = '%s%s' % (gravatar_cdn, _get_gravatar(i['author__email']))

    context = {
        'articles': articles,

    }

    return render(request, "all-articles.html", context=context)


def one_article(request, article_id):
    try:
        article = Article.objects.get(tid=article_id)

        comments = Reply.objects.filter(topic=article)\
        .values('rid', 'content', 'author__email', 'time', 'author__username', 'to_reply', 'to_user__username')
    except Article.DoesNotExist:
        return HttpResponse('404 not found')

    article.gravatar = '%s%s' % (gravatar_cdn, _get_gravatar(article.author.email))

    comment_dict = collections.OrderedDict()

    for i in comments:
        i['gravatar'] = '%s%s' % (gravatar_cdn, _get_gravatar(i['author__email']))
        if i['to_reply'] is None:
            comment_dict[i['rid']] = i
            comment_dict[i['rid']]['reply_list'] = list()
        else:
            comment_dict[i['to_reply']]['reply_list'].append(i)

    for i in comment_dict:
        print comment_dict[i]

    context = {
        'article': article,
        'comments': comment_dict
    }

    return render(request, "one-articles.html", context=context)


def _get_gravatar(email):
    md5 = hashlib.md5()
    md5.update(email)
    return str(md5.hexdigest())
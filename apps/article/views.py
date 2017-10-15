from django.shortcuts import render
from django.db.models import Count
from apps.article.models import Article, Reply
from apps.account.models import User
from django.http.response import JsonResponse, HttpResponse
from const import gravatar_cdn
import collections
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from apps.manager.OssSaver import OssSaver

import hashlib
import shortuuid
import uuid
from django.utils import timezone


def get_articles(request):
    offset = request.GET.get("offset", 0)
    articles = Article.objects.all().annotate(comment_count=Count('reply')) \
                   .values('tid', 'content', 'title', 'author__email', 'author__username', 'updated_at',
                           'comment_count') \
                   .order_by("-updated_at")[:15]

    for i in articles:
        i['gravatar'] = '%s%s' % (gravatar_cdn, _get_gravatar(i['author__email']))

        if len(i['content']) > 400:
            i['content'] = i['content'][:400]

    context = {
        'articles': articles,
    }

    return render(request, "all-articles.html", context=context)


def one_article(request, article_id):
    try:
        article = Article.objects.get(tid=article_id)

        comments = Reply.objects.filter(topic=article) \
            .values('rid', 'content', 'author__email', 'time', 'author__username', 'to_reply', 'to_user__username')
        print comments.query
    except Article.DoesNotExist:
        return HttpResponse('404 not found')

    article.gravatar = '%s%s' % (gravatar_cdn, _get_gravatar(article.author.email))

    comment_dict = collections.OrderedDict()

    for i in comments:
        i['gravatar'] = '%s%s' % (gravatar_cdn, _get_gravatar(i['author__email']))
        print('i-to reply',i['to_reply'])
        print('i', i)
        print('i-rid', i['rid'])
        if i['to_reply'] is None:
            comment_dict[i['rid']] = i
            comment_dict[i['rid']]['reply_list'] = list()
        else:
            comment_dict[i['to_reply']]['reply_list'].append(i)
            #print(comment_dict)

    context = {
        'article': article,
        'comments': comment_dict
    }

    return render(request, "one-articles.html", context=context)


def _get_gravatar(email):
    md5 = hashlib.md5()
    md5.update(email)
    return str(md5.hexdigest())


@login_required
def post_receiver(request):
    response = {
        'status': 200,
        'message': 'ok'
    }
    content = request.POST.get('content', '')
    if not request.POST.has_key('title'):
        if not request.POST.has_key('commentType'):
            return JsonResponse({
                'status': 500,
                'message': 'Article title required.'
            })
        else:
            if not request.POST.has_key('commentId'):
                return JsonResponse({
                    'status': 500,
                    'message': 'Comment id required.'
                })
            comment_type = request.POST.get('commentType', None)
            if comment_type not in ['a', 'c', 'r']:
                return JsonResponse({
                    'status': 500,
                    'message': 'Comment type unsupported.'
                })
            comment_id = request.POST.get('commentId', None)

            if comment_type == 'a':
                to_user = None
                to_reply = None
                topic = Article.objects.get(tid=comment_id)
            else:
                comment = Reply.objects.get(rid=comment_id)
                to_user = comment.author
                topic = comment.topic
                if comment_type == 'c':
                    to_reply = comment
                else:
                    to_reply = comment.to_reply

            reply = Reply(
                author=request.user,
                author_username=request.user.username,
                to_user=to_user,
                time=timezone.now(),
                content=content,
                topic=topic,
                to_reply=to_reply,
                status=0
            )
            reply.save()
            return JsonResponse({
                'status':200
            })

    else:
        title = request.POST.get('title', '')
        if title == '':
            return JsonResponse({
                'status': 500,
                'message': 'Article title required.'
            })

        article_type = request.POST.get('type', 0)
        pid = 0
        if article_type == 0:
            pass
        else:
            pid = request.POST.get('pid', None)
            print(pid)
            if not pid:
                return JsonResponse({
                    'status': 500,
                    'message': 'problem id required.'
                })
        try:
            article = Article(
                content=content,
                pid=pid,
                title=title,
                author=request.user,
                updated_at=timezone.now(),
                status=0,
                top_level=0
            )
            article.save()
        except:
            response['status'] = 500
            response['message'] = 'unknown error.'

        return JsonResponse(response)


@login_required
@csrf_exempt
def image_receiver(request):
    if len(request.FILES) > 1:
        return JsonResponse({'status': 500, 'message': 'only one file accepted'})

    for one_file_name in request.FILES:
        one_file = request.FILES[one_file_name]
        oss_saver = OssSaver()
        file_name = 'article/{0}/{1}/{2}'.format(request.user.username, shortuuid.encode(uuid.uuid1()), one_file._name)
        file_url = oss_saver.upload_file(one_file, file_name, one_file.content_type)

        return JsonResponse({
            'status': 200,
            'massage': 'ok',
            'data': {
                'url': file_url
            }
        })

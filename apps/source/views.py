import uuid
import shortuuid
import time
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.http import HttpResponseRedirect
from django.core.exceptions import *
from django.core.urlresolvers import reverse
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from models import OnlySourceCode
from models import OjSourceCode
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.lexers._mapping import LEXERS
from apps.status.models.Solution import Solution
from const import language_name, code_source_style


def get_fullname_by_aliasname(alias):
    for index in LEXERS:
        for a in LEXERS[index][2]:
            if a == alias:
                return LEXERS[index][1]
    return 'No Such Name!'


def render_source_page(request, poster, self_url, height_style, style_sheet, source, lang, poster_time, use_time, _url):
    size = round(len(source.encode("utf-8")) / float(1000), 3)
    context = dict(
        style_sheet=style_sheet,
        source=source,
        lang=lang,
        time=poster_time,
        use_time=use_time,
        size=size,
        poster=poster,
        self_url=self_url,
        styles=code_source_style,
        this_style=height_style,
        url=_url,
    )

    return render(request, 'show-source.html', context=context)


def render_source_file(request, stream, file_name, content_type='text/plain'):
    response = StreamingHttpResponse(stream, content_type=content_type)
    response['Content-Disposition'] = 'attachment;filename=\"' + file_name + '\"'
    return response


def render_qrcode(request, data):
    import qrcode
    import cStringIO

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=12,
        border=0
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image()
    output = cStringIO.StringIO()
    img.save(output)
    contents = output.getvalue()
    output.close()
    return HttpResponse(contents, content_type='image/png')


@cache_page(10)
def source_by_uuid(request, user_uuid):
    height_style = request.GET.get('style', 'monokai')

    try:
        only_source_code = OnlySourceCode.objects.get(uuid=user_uuid)
    except ObjectDoesNotExist:
        return HttpResponse(u'no such source code.', status=404)

    if 'file' in request.GET:
        if request.GET.get('file') == 'as_txt_file':
            file_name = only_source_code.poster + '.txt'
        else:
            file_name = only_source_code.poster
        return render_source_file(request, only_source_code.source, file_name)

    _url = request.get_host() + reverse('only_source_by_uuid', args=[user_uuid, ])
    if request.is_secure():
        _url = u'https://' + _url
    else:
        _url = u'http://' + _url

    if 'qrcode' in request.GET:
        return render_qrcode(request, _url)

    lang_alias = only_source_code.lexer
    poster = only_source_code.poster
    lexer = get_lexer_by_name(lang_alias)
    source = only_source_code.source

    start_time = time.time()
    style_sheet = HtmlFormatter(
        linenos=True,
        style=height_style,
    ).get_style_defs('.highlight')
    source = highlight(source, lexer, HtmlFormatter(
        linenos=True,
        style=height_style,
    ))
    lang = get_fullname_by_aliasname(lang_alias)

    used_time = round((time.time() - start_time)*1000, 2)

    return render_source_page(request, poster, user_uuid, height_style, style_sheet,
                              source, lang, only_source_code.created_at, used_time, _url)

@cache_page(3)
@login_required(redirect_field_name='from_url')
def source_by_run_id(request, run_id):
    try:
        solution = Solution.objects.get(solution_id=run_id)
    except Solution.DoesNotExist:
        return HttpResponse('not found such solution', status=404)

    if solution.user_id != request.user.username and not request.user.is_superuser:
        return HttpResponse('do not have permissions', status=304)

    height_style = request.GET.get('style', 'monokai')

    try:
        source_code = OjSourceCode.objects.get(solution_id=run_id)
    except ObjectDoesNotExist:
        return HttpResponse('no this problem', status=404)

    if 'file' in request.GET:
        if request.GET.get('file') == 'as_txt_file':
            file_name = 'oj-'+run_id+'.txt'
        else:
            file_name = 'oj-'+run_id
        return render_source_file(request, source_code.source, file_name)

    _url = request.get_host() + reverse('only_source_by_run_id', args=[run_id, ])
    if request.is_secure():
        _url = 'https://' + _url
    else:
        _url = 'http://' + _url

    if 'qrcode' in request.GET:
        return render_qrcode(request, _url)

    poster = solution.user_id

    if solution.judge_type ==0:
        lang = language_name[solution.language]
        if 13 <= solution.language <=14:
            standard_lang = 'C++'
        elif solution.language == 6:
            standard_lang = 'Python'
        elif solution.language == 3:
            standard_lang = 'Java'
        elif solution.language == 16:
            standard_lang = 'JavaScript'
        elif solution.language == 17:
            standard_lang = 'Python3'
        else:
            standard_lang = lang
    else:
        lang = solution.language_name
        if solution.language_name == 'G++':
            standard_lang = 'C++'
        elif solution.language_name == 'GCC':
            standard_lang = 'C'
        else:
            standard_lang = solution.language_name

    lexer = get_lexer_by_name(standard_lang)
    source = source_code.source

    start_time = time.time()
    style_sheet = HtmlFormatter(
        linenos=True,
        style=height_style
    ).get_style_defs('.highlight')
    source = highlight(source, lexer, HtmlFormatter(
        linenos=True,
        style=height_style
    ))
    use_time = round((time.time() - start_time)*1000, 2)

    return render_source_page(request, poster, run_id, height_style, style_sheet,
                              source, lang, solution.in_date, use_time, _url)


def put_source(request):
    if request.method == 'POST':
        poster = request.POST.get('poster', '').encode('utf-8')
        lang = request.POST.get('lang', 'text')
        source = request.POST.get('source', '')

        if poster == '' or source == '':
            return HttpResponse('error params')

        user_uuid = shortuuid.encode(uuid.uuid1())

        only_source_code = OnlySourceCode(
            uuid=user_uuid,
            poster=poster,
            lexer=lang,
            source=source,
        )

        only_source_code.save()

        return HttpResponseRedirect(reverse('only_source_by_uuid', args=[user_uuid, ]))
    else:
        return render(request, 'put-source.html')



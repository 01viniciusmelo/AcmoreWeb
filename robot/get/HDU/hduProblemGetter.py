from get.problemSaver import ProblemSaver
from bs4 import BeautifulSoup
import urllib2
import json
import time

from get.OssSaver import OssSaver


class HduProblemGetter():
    def __init__(self, pid):
        self.problem_id = pid
        self.problem_url = 'http://acm.hdu.edu.cn/showproblem.php?pid='+str(pid)
        self.headers = {
            'Host':'acm.hdu.edu.cn',
            'Origin':'http://acm.hdu.edu.cn',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language':'en,zh;q=0.8,zh-CN;q=0.6',
            'Connection':'keep-alive',
            'Cache-Control':'max-age=0',
            'Content-Type':'application/x-www-form-urlencoded',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
        }
        self.oss = OssSaver()
        self.hdu_mirror_url = 'http://acm.hdu.edu.cn'

    def get(self):

        request = urllib2.Request(self.problem_url, headers=self.headers)
        response = urllib2.urlopen(request)

        response_string = response.read()

        if '<DIV>No such problem - <strong>Problem %s</strong>.</DIV>' % self.problem_id in response_string:
            print('No such problem(id:%s) on HDU.' % self.problem_id)
            return 0

        soup = BeautifulSoup(response_string, 'html5lib')

        content = soup.find_all('td', align='center')[2]
        panel_titles = content.select('.panel_title')
        panels = content.select(".panel_content")

        title = content.find('h1').string

        data = dict()

        for item in zip(panel_titles, panels):
            data[item[0].string] = item[1].decode_contents(formatter='html')

        if 'Problem Description' in data:
            desc = data['Problem Description']
            del(data['Problem Description'])
        else:
            desc = ''

        if 'Input' in data:
            _input = data['Input']
            del(data['Input'])
        else:
            _input = ''

        if 'Output' in data:
            _output = data['Output']
            del(data['Output'])
        else:
            _output = ''

        if 'Sample Input' in data:
            sample_input_bs = BeautifulSoup(data['Sample Input'], 'lxml')
            sample_input = sample_input_bs.div.decode_contents(formatter='html')
            del(data['Sample Input'])
        else:
            sample_input = ''

        if 'Sample Output' in data:
            sample_output_bs = BeautifulSoup(data['Sample Output'], 'lxml')
            sample_output = sample_output_bs.div.decode_contents(formatter='html')
            del(data['Sample Output'])
        else:
            sample_output = ''

        if 'Source' in data:
            source = data['Source']
            del(data['Source'])
        else:
            source = ''

        def change_html_img_src_to_absolute(html_content, parser='lxml'):
            html_bs = BeautifulSoup(html_content, parser)
            if html_bs.find('img') is not None:
                for image_tag in html_bs.find_all('img'):
                    if 'http' in image_tag.attrs['src']:
                        file_url = image_tag.attrs['src']
                    else:
                        file_url = self.hdu_mirror_url + image_tag.attrs['src']
                    file_url = file_url.replace('../', '/')

                    image_tag.attrs['src'] = self.oss.upload_file_from_url(file_url, diy_prefix='hdu/%s/'%self.problem_id)

                return html_bs.decode_contents(formatter="html")
            return html_content


        desc = change_html_img_src_to_absolute(desc)

        _input = change_html_img_src_to_absolute(_input)

        _output = change_html_img_src_to_absolute(_output)

        sample_input = change_html_img_src_to_absolute(sample_input)

        sample_output = change_html_img_src_to_absolute(sample_output)

        if source != '':
            source_bs  = BeautifulSoup(source, 'lxml')
            source_arr = source_bs.strings
            source = ''
            for i in source_arr:
                source = source + i


        attr_content = content.find('font').b.span.decode_contents(formatter='html')

        attr_array = attr_content.split('<br/>')

        spj = 0
        if len(attr_array) > 2:
            if 'Special Judge' in attr_array[2]:
                spj = 1

        time_and_memory_limit_info = attr_array[0].split('&nbsp;&nbsp;&nbsp;&nbsp;')
        time_limit = time_and_memory_limit_info[0].split(':')[1]
        memory_limit = time_and_memory_limit_info[1].split(':')[1]

        attr = dict(
            a=dict(),
            d=data
        )

        attr = json.dumps(attr)

        problem = ProblemSaver(
            description=desc.encode('utf-8'),
            title=title.encode('utf-8'),
            attrs=attr.encode('utf-8'),
            _input=_input.encode('utf-8'),
            _output=_output.encode('utf-8'),
            sample_input=sample_input.encode('utf-8'),
            sample_output=sample_output.encode('utf-8'),
            problem_id=self.problem_id,
            judge_name='HDU'.encode('utf-8'),
            source=source,
            time_limit=time_limit,
            memory_limit=memory_limit,
            spj=spj
        )

        problem.save()

from bs4 import BeautifulSoup
from submit.Submitter import Submitter
import urllib
import urllib2
import json
import time


class HduProblemSubmitter(Submitter):
    def __init__(self, solution_id, problem_id, language):
        Submitter.__init__(self)

        print solution_id, problem_id, language

        self.solution_id = solution_id
        self.problem_id = problem_id
        self.language = language

        self.hdu_base_url = 'http://acm.hdu.edu.cn/'
        self.login_url = self.hdu_base_url + 'userloginex.php?action=login&cid=0&notice=0'
        self.submit_url = self.hdu_base_url + 'submit.php?action=submit'
        self.status_url = self.hdu_base_url + 'status.php?user='

        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
        }

        cookies = urllib2.HTTPCookieProcessor()
        self.opener = urllib2.build_opener(cookies)
        self.v_judge_username = ''

    def submit(self):
        sql = 'SELECT `username`,`password` FROM `vjudge_user` WHERE `using`=0 AND `judge_name`="HDU" LIMIT 1;'

        self.cur.execute(sql)

        result = self.cur.fetchone()

        if result is None:
            print 'All account is in using now, please retry later.'
            return False

        post_data = dict(
            username=result[0],
            userpass=result[1],
        )
        self.v_judge_username = result[0]

        self.status_url = self.status_url + result[0]

        request = urllib2.Request(self.login_url, data=urllib.urlencode(post_data), headers=self.headers)

        try:
            self.opener.open(request)
        except urllib2.URLError, e:
            if hasattr(e, 'code'):
                print 'Error code: ', e.code
            elif hasattr(e, 'reason'):
                print 'login failed.'
                print 'Reason: ', e.reason
        else:
            sql = 'SELECT * FROM `source_code_user` WHERE `solution_id`=%s;' % self.solution_id

            self.cur.execute(sql)

            values = {
                'language':self.language,
                'usercode':self.cur.fetchone()[1].encode('utf-8'),
                'problemid':self.problem_id
            }

            post_data = urllib.urlencode(values)
            request = urllib2.Request(self.submit_url, post_data, self.headers)

            try:
                response = self.opener.open(request)
            except urllib2.URLError:
                print 'submit failed'
                return False
            else:
                html_content = response.read()
                if '<h1>Realtime Status</h1>' in html_content:
                    return True, False, 'success'
                elif 'Code length is improper' in html_content:
                    return False, False, 'Code too short'
                else:
                    return False, True, 'retry later'


    def vjudge_id(self):
        request = urllib2.Request('%s&pid=%s' % (self.status_url, self.problem_id), headers=self.headers)

        retry_times = 3
        for i in xrange(retry_times):
            try:
                response = self.opener.open(request)
            except urllib2.URLError:
                print 'get status failed'
            else:
                soup = BeautifulSoup(response, 'html5lib')

                return soup.find('table', class_='table_text').find('tr', align='center').find('td').string

            time.sleep(1)

        return False

    def v_username(self):
        return self.v_judge_username
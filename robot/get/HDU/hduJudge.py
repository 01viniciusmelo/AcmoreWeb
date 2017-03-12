from bs4 import BeautifulSoup
import urllib
import urllib2
import json
import time

class HduJudge:
    def __init__(self, v_judge_id):
        self.v_judge_id = v_judge_id
        hdu_base_url = 'http://acm.hdu.edu.cn/'
        self.status_url = hdu_base_url + 'status.php?first=' + str(v_judge_id)
        self.view_error_url = hdu_base_url + 'viewerror.php?rid=' + str(v_judge_id)
        self.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
        }

        cookies = urllib2.HTTPCookieProcessor()
        self.opener = urllib2.build_opener(cookies)

    def status(self):
        request = urllib2.Request(self.status_url, headers=self.headers)
        response = self.opener.open(request)

        soup = BeautifulSoup(response, 'html5lib')

        status_td_list = soup.find('table', class_='table_text').find('tr', align='center').find_all('td')
        status_string = status_td_list[2].font.text
        time_used = status_td_list[4].text.replace('MS', '')
        memory_used = status_td_list[5].text.replace('K', '')

        if status_string == 'Queuing':
            response = (1, 'v-waiting')
        elif status_string == 'Compiling':
            response = (2, None)
        elif status_string == 'Running':
            response = (3, None)
        elif status_string == 'Accepted':
            response = (4, None)
        elif status_string == 'Presentation Error':
            response = (5, None)
        elif status_string == 'Wrong Answer':
            response = (6, None)
        elif 'Runtime Error' in status_string:
            response = (10, status_string)
        elif 'Time Limit Exceeded' in status_string:
            response = (7, None)
        elif 'Memory Limit Exceeded' in status_string:
            response = (8, None)
        elif 'Output Limit Exceeded' in status_string:
            response = (9, None)
        elif 'Compilation Error' in status_string:
            response = (11, None)
        elif 'System Error' in status_string:
            response = (6, 'System Error')
        elif 'Out Of Contest Time' in status_string:
            response = (6, 'Out Of Contest Time')
        else:
            response = (6, 'No status')

        response = response + (time_used, memory_used)
        print(status_string, response)
        return response

    def get_error_info(self):
        request = urllib2.Request(self.view_error_url, headers=self.headers)
        retry_times = 3
        while True:
            print 'get error info times: ', retry_times
            try:
                response = self.opener.open(request)
            except:
                time.sleep(0.5)
                retry_times = retry_times - 1
                if retry_times > -1:
                    continue
                else:
                    return 'Sorry, get error info failed.'
            else:
                err_content = BeautifulSoup(response, 'lxml').find('pre').text
                return err_content





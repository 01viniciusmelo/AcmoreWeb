from get.HDU.hduProblemGetter import HduProblemGetter
from get.DBHelper import Saver
from bs4 import BeautifulSoup
import urllib2


class Checker(Saver):
    def __init__(self):
        Saver.__init__(self)
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
        self.hdu_base_url = 'http://acm.hdu.edu.cn/'

    def db_last_problem_id(self):
        sql = 'SELECT `problem_id` FROM problem ORDER BY `problem_id` DESC limit 1;'
        self.cur.execute(sql)
        return int(self.cur.fetchone()[0])

    def hdu_last_problem_id(self):
        hdu_problem_list_page_number = self.__hdu_list_page_number()
        hdu_problem_list_page_url = '%slistproblem.php?vol=%s' % (self.hdu_base_url, hdu_problem_list_page_number)

        one_request = urllib2.Request(hdu_problem_list_page_url, headers=self.headers)
        one_response = urllib2.urlopen(one_request)

        soup = BeautifulSoup(one_response.read(), 'html5lib')
        return int(soup.find_all('script', language='javascript')[1].get_text().split(';p(')[-1].split(',')[1])

    def __hdu_list_page_number(self):
        hdu_problem_list_page_url = 'http://acm.hdu.edu.cn/listproblem.php?vol=1'
        one_request = urllib2.Request(hdu_problem_list_page_url, headers=self.headers)
        one_response = urllib2.urlopen(one_request)
        soup = BeautifulSoup(one_response.read(), 'html5lib')
        return soup.find_all("a", style='margin:5px')[-1].get_text()



checker = Checker()
hdu_db_last_problem_id = checker.hdu_last_problem_id()
db_last_problem_id = checker.db_last_problem_id()

for problem_id in range(db_last_problem_id, hdu_db_last_problem_id):
    getter = HduProblemGetter(problem_id)
    getter.get()



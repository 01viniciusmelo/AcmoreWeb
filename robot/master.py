from submit.Submitter import Submitter
from submit.HDU.hduSubmitter import HduProblemSubmitter
from get.HDU.hduJudge import HduJudge
import MySQLdb
import time


class Master(Submitter):
    def __init__(self):
        Submitter.__init__(self)
        self.do()

    def do(self):
        while True:
            solution = self.__get_submit_mission()

            if solution is not None:
                if solution['judge_name'] == 'HDU':
                    submitter = HduProblemSubmitter(solution['solution_id'], solution['problem_id'], solution['language'])

                    submit_ok, retry, message = submitter.submit()
                    if submit_ok:
                        vjudge_id = submitter.vjudge_id()
                        if vjudge_id != False:
                            self.__update_submit_mission(solution['solution_id'], submitter.v_username(),vjudge_id)
                        else:
                            print 'get vjudge submit id failed, retry later.'
                    else:
                        if retry:
                            print 'submit failed, retry later.'
                        else:
                            self.__update_submit_mission(solution['solution_id'], submitter.v_username(), result=6, result_name=message)
            else:
                pass

            solution = self.__get_update_status_mission()
            if solution is not None:
                if solution['vjudge_solution_id'] is None or solution['vjudge_solution_id'] == '':
                    pass
                else:
                    if solution['judge_name'] == 'HDU':
                        v_judge = HduJudge(solution['vjudge_solution_id'])
                        v_status = list(v_judge.status())

                        self.__update_update_status_mission(solution['solution_id'], v_status[0], v_status[1])
                        if v_status[0] == 11:
                            error = v_judge.get_error_info()
                            self.__update_compile_info(solution['solution_id'], error)
            else:
                pass

            time.sleep(0.8)

    def __get_submit_mission(self):
        sql = 'SELECT `solution_id`,`problem_id`,`language`,`judge_name` FROM `solution` WHERE `judge_name`!="LOCAL" AND `result`=0 LIMIT 1;'
        cur = self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        cur.execute(sql)
        return cur.fetchone()

    def __update_submit_mission(self,solution_id,v_judge_user,v_solution_id='',result=2,result_name='Submitted'):
        sql = 'UPDATE `solution` SET `vjudge_solution_id`=%s, `result`=%s, `result_name`=%s, `judger`=%s WHERE `solution_id`=%s;'
        self.cur.execute(sql, (v_solution_id, result, result_name, v_judge_user, solution_id))

    def __get_update_status_mission(self):
        sql = 'SELECT `solution_id`,`judge_name`,`vjudge_solution_id` FROM `solution` WHERE `judge_type`=1 AND `result`<4 LIMIT 1;'
        cur = self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        cur.execute(sql)
        return cur.fetchone()

    def __update_update_status_mission(self, solution_id, result, result_name):
        sql = 'UPDATE `solution` SET `result`=%s,`result_name`=%s WHERE `solution_id`=%s;'
        self.cur.execute(sql, (result, result_name, solution_id))

    def __update_compile_info(self, solution_id, error):
        sql = 'INSERT INTO `compileinfo` (`solution_id`, `error`) VALUES (%s, %s);'
        self.cur.execute(sql, (solution_id, error.encode('utf-8')))


master = Master()

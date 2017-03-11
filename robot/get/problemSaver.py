import datetime
from Saver import Saver


class ProblemSaver(Saver):
    def __init__(self,problem_id,in_date=datetime.datetime.utcnow(),judge_name=None,title='',description='',
                 _input='',_output='',sample_input='',sample_output='',spj=0,hint='',source='',time_limit=-1,memory_limit=-1,defunct='N',accepted=0,submit=0,solved=0,attrs=''):
        Saver.__init__(self)

        self.problem_id = problem_id
        self.title = title
        self.description = description
        self.input = _input
        self.output = _output
        self.sample_input = sample_input
        self.sample_output = sample_output
        self.spj = spj
        self.hint = hint
        self.source = source
        self.in_date = in_date
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.defunct = defunct
        self.accepted = accepted
        self.submit = submit
        self.solved = solved
        self.judge_name = judge_name
        self.attrs = attrs

    def save(self):
        if self.judge_name is None:
            print("judge name can not be None")
        else:
            print(self.judge_name, self.problem_id)

            sql = 'SELECT COUNT(*) FROM `problem` AS t WHERE t.judge_name=%s AND t.problem_id=%s;'
            self.cur.execute(sql, (self.judge_name, self.problem_id, ))

            if self.cur.fetchone()[0] > 0:
                print('problem %s - %s already exited, update now.' % (self.judge_name, self.problem_id))
                sql = 'UPDATE `problem` SET' \
                      '`problem_id`=%s,`title`=%s,`description`=%s,`input`=%s,`output`=%s,' \
                      '`sample_input`=%s,`sample_output`=%s,`spj`=%s,`hint`=%s,`source`=%s,' \
                      '`in_date`=%s,`time_limit`=%s,`memory_limit`=%s,`defunct`=%s,`accepted`=%s,' \
                      '`submit`=%s,`solved`=%s,`judge_name`=%s,`attrs`=%s WHERE `problem_id`=%s ' \
                      'AND `judge_name`=%s;'

                self.cur.execute(sql, (self.problem_id,self.title,self.description,self.input,self.output,
                                       self.sample_input,self.sample_output,self.spj,self.hint,self.source,self.in_date,
                                       self.time_limit,self.memory_limit,self.defunct,self.accepted,self.submit,self.solved,
                                       self.judge_name,self.attrs,self.problem_id, self.judge_name))
                print('update %s success.' % self.problem_id)

            else:
                sql = 'INSERT INTO `problem`' \
                      '(`problem_id`,`title`,`description`,`input`,`output`,`sample_input`,`sample_output`,' \
                      '`spj`,`hint`,`source`,`in_date`,`time_limit`,`memory_limit`,`defunct`,`accepted`,' \
                      '`submit`,`solved`,`judge_name`, `attrs`) VALUES ' \
                      '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

                self.cur.execute(sql, (self.problem_id,self.title,self.description,self.input,self.output,
                                        self.sample_input,self.sample_output,self.spj,self.hint,self.source,self.in_date,
                                        self.time_limit,self.memory_limit,self.defunct,self.accepted,self.submit,self.solved,
                                        self.judge_name,self.attrs))

                print('insert %s - %s success.' % (self.judge_name, self.problem_id))

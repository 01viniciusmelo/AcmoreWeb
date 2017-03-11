from Saver import Saver


class LanguageSaver(Saver):
    def __init__(self,language_id,language_name,judge_name,enabled=1):
        Saver.__init__(self)

        self.language_id = language_id
        self.language_name = language_name
        self.judge_name = judge_name
        self.enabled = enabled

    def save(self):
        if self.language_id is None or self.language_name is None or self.judge_name is None:
            print("params required not filled.")
        else:
            sql = 'SELECT COUNT(*) FROM `judge_language` AS t WHERE t.language_id=%s AND t.judge_name=%s;'
            self.cur.execute(sql, (self.language_id,self.judge_name))

            if self.cur.fetchone()[0] > 0:
                print('language id %s already exited, name is %s update now.' % (self.language_id, self.language_name))
                sql = 'UPDATE `judge_language` SET ' \
                      '`language_name`=%s,`judge_name`=%s,`enabled`=%s ' \
                      'WHERE `language_id`=%s;'

                self.cur.execute(sql, (self.language_name,self.judge_name,self.enabled,self.language_id))
                print('update %s success, judge name is %s' % (self.language_name, self.judge_name))

            else:
                sql = 'INSERT INTO `judge_language` ' \
                      '(`language_id`, `language_name`,`judge_name`,`enabled`) VALUES ' \
                      '(%s, %s, %s, %s)'

                self.cur.execute(sql, ((self.language_id,self.language_name,self.judge_name,self.enabled)))

                print('insert %s - %s success.' % (self.language_name, self.judge_name))

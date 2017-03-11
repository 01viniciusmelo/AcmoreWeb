from setting import *
import MySQLdb


class Submitter:
    def __init__(self):
        self.conn = MySQLdb.connect(db=db_name,host=db_host,user=db_username,passwd=db_password,charset=db_charset)
        self.cur = self.conn.cursor()
        self.conn.autocommit(True)
        self.cur.execute('SET character_set_connection=utf8,collation_connection=utf8_unicode_ci;')

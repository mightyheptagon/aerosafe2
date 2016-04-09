# A wrapper around MySQLdb
# To start querying you need to open a connection
###     cnx = db.connect()
# There are 2 types of queries: query (for queries that return stuff) and mutate (for queries that mutate tables and databases)
# As soon as you finish querying call
# db.close(cnx) !!!! (IMPORTANT)

import MySQLdb
from credentials import get_credentials

config = {
    'user': 'aero',
    'passwd': get_credentials(),
    'host': '127.0.0.1',
    'port': 3306,
    'db': 'aerotest'
}

import MySQLdb.cursors


class MySQLCursorDict(MySQLdb.cursors.Cursor):

    def fetchone(self):
        row = self._fetch_row()
        if row:
            return dict(zip(self.column_names, self._row_to_python(row)))
        return None


class Connection():

    def __init__(self):
        self.cnx = None

    def __enter__(self):
        self.cnx = connect()
        return self.cnx

    def __exit__(self, type, value, traceback):
        close(self.cnx)


def connect():
    cnx = None
    try:
        cnx = MySQLdb.connect(**config)
        print '[DBO] DB Connection established.'
        return cnx
    except Exception as err:
        print err
        cnx.close()


def close(cnx):
    try:
        cnx.close()
        print '[DBO] DB Connect closed.'
    except Exception as e:
        pass


def query(cnx, query, param=None):
    try:
        result = []
        cursor = cnx.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute(query, param)
        out = cursor.fetchall()
        return out
    except Exception as e:
        # error
        raise e

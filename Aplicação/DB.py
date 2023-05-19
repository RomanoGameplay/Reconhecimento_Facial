import sqlite3 as sql
import os


class DataBase:
    def __init__(self, check_same_thread=False):
        try:
            self._db_file = 'DB_Alunos.db'
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(BASE_DIR, self._db_file)
            self._connection = sql.connect(db_path, check_same_thread=check_same_thread)
        except sql.Error as err:
            print(err)
        else:
            self._cursor = self._connection.cursor()

    def get_cursor(self):
        return self._cursor

    def get_connection(self):
        return self._connection

    def close(self):
        self._connection.close()
        print('Banco de dados fechado com sucesso!')

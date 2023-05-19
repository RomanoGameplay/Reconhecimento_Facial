from DB import DataBase
from datetime import datetime
import sqlite3 as sql
import pandas as pd
import stat
import os


class TableMissings(DataBase):
    def __init__(self, check_same_thread=False):
        super().__init__(check_same_thread)
        self._cursor = self.get_cursor()
        self._connection = self.get_connection()
        self._table_name_morning = 'FaltantesManha'
        self._table_name_afternoon = 'FaltantesTarde'

        query = self._create_query()
        self._create_table_missings(query, self._table_name_morning)
        self._create_table_missings(query, self._table_name_afternoon)

    def _create_query(self):
        query = """
                                create table if not exists []
                                (
                                ID INTEGER not null constraint ID primary key autoincrement,
                                Aluno_ID TEXT not null,
                                Dia TEXT not null,
                                UNIQUE(Aluno_ID, Dia)
                                )
                                """
        return query

    def _create_table_missings(self, query, table):
        try:
            query = query.replace('[]', table)
            self._cursor.execute(query)
        except sql.Error as err:
            print(err)
        else:
            self._connection.commit()

    def _insert(self, table, aluno_id=None, date_missing=None):
        try:
            self._cursor.execute(
                f"""INSERT INTO {table} (Aluno_ID, Dia) VALUES (?, ?)""",
                (
                    str(aluno_id), str(date_missing),))
        except sql.IntegrityError:
            pass
        except sql.Error as err:
            print(err)
        else:
            self._connection.commit()

    def insert_data_into_table(self, table, period):
        with open('schedules.json', 'r') as json_arquive:
            current_date = datetime.now().strftime('%d/%m/%Y')
            missings = self._get_missings(table=table, period=period)

        if period == 'MANHÃ':
            table = self._table_name_morning

        elif period == 'TARDE':
            table = self._table_name_afternoon

        for missing in missings:
            self._insert(table=table, aluno_id=missing[0], date_missing=current_date)

    def read(self, table):
        self._cursor.execute(f"""select * from {table};""")
        return list(self._cursor.fetchall())

    def export_table_to_csv(self, table):
        try:
            path = f'Backup_DataBase/Backup_{table}.csv'
            if os.path.exists(path):
                os.remove(path)
            missings = pd.read_sql(f'SELECT * FROM {table}', self._connection)
            missings.to_csv(path, index=False)
            os.chmod(path, stat.S_IREAD)
        except Exception as err:
            print(err)
            print(f'\nErro na exportação da tabela {table}!\n')

    def delete_all_data(self, table='*'):
        try:
            query_manha = f'delete from {self._table_name_morning};'
            query_tarde = f'delete from {self._table_name_afternoon};'
            if table == '*':
                self._cursor.execute(query_manha)
                self._cursor.execute(query_tarde)

            elif table == self._table_name_morning:
                self._cursor.execute(query_manha)

            elif table == self._table_name_afternoon:
                self._cursor.execute(query_tarde)

        except sql.Error as e:
            print(e)
        else:
            self._connection.commit()

    def table_to_sql(self, table):
        if os.path.exists(f'Backup_DataBase/Backup_{table}.csv'):
            missings = pd.read_csv(f'Backup_DataBase/Backup_{table}.csv', engine='c')
            missings.to_sql(table, con=self._connection, if_exists='replace', index=False)
        else:
            print(f'Não existe backup da tabela {table}!')

    def import_backup_tables_missings(self, table='*'):
        if table == '*':
            self.table_to_sql(table=self._table_name_morning)
            self.table_to_sql(table=self._table_name_afternoon)

        elif table == self._table_name_morning:
            self.table_to_sql(table=self._table_name_morning)
        elif table == self._table_name_afternoon:
            self.table_to_sql(table=self._table_name_afternoon)

    def _get_missings(self, table, period):
        query = f"""
                            SELECT Cadastrados.ID
                            FROM Cadastrados where Cadastrados.PeriodoEscolar = "{period}"
                            EXCEPT
                            SELECT CAST({table}.Aluno_ID AS INTEGER)
                            FROM {table} where {table}.Dia = "{datetime.now().strftime('%d/%m/%Y')}";
                        """
        missings = self._cursor.execute(query).fetchall()
        return missings

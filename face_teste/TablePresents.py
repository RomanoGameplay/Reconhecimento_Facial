from DB import DataBase
import pandas as pd
import sqlite3 as sql
import os
import stat


class TablePresents(DataBase):
    def __init__(self, check_same_thread=False):
        super().__init__(check_same_thread)
        self._cursor = self.get_cursor()
        self._connection = self.get_connection()
        self._table_name_morning = 'PresentesManha'
        self._table_name_afternoon = 'PresentesTarde'

        self._create_table_presents(self._table_name_morning)
        self._create_table_presents(self._table_name_afternoon)

    def _create_table_presents(self, table):
        try:
            self._cursor.execute(f"""
                create table if not exists {table}
                (
                ID INTEGER not null constraint ID primary key autoincrement,
                Aluno_ID TEXT not null,
                Dia TEXT not null,
                Horas TEXT not null,
                UNIQUE(Aluno_ID, Dia)
                )
                """)
        except sql.Error as err:
            print(err)
        else:
            self._connection.commit()

    def insert(self, table, aluno_id=None, date_present=None, hours=None):
        try:
            self._cursor.execute(f"""
            INSERT INTO {table} (Aluno_ID, Dia, Horas) VALUES (?, ?, ?)
            """, (str(aluno_id), str(date_present), str(hours)))
        except sql.IntegrityError:
            pass
        except Exception as err:
            print(err)
            print(f'\nErro na inserção de presenca na tabela {table}!\n')
        else:
            self._connection.commit()

    def read(self, table):
        self._cursor.execute(f"""select * from {table};""")
        return list(self._cursor.fetchall())

    def export_table_to_csv(self, table):
        try:
            path = f'Backup_DataBase/Backup_{table}.csv'
            if os.path.exists(path):
                os.remove(path)
            presents = pd.read_sql(f'SELECT * FROM {table}', self._connection)
            presents.to_csv(path, index=False)
            os.chmod(path, stat.S_IREAD)
        except Exception as err:
            print(err)
            print(f'\nErro na exportação da tabela {table}!\n')

    def delete_all_data(self, table='*'):
        try:
            query_delete_morning = f'delete from {self._table_name_morning};'
            query_delete_afternoon = f'delete from {self._table_name_afternoon};'
            if table == '*':
                self._cursor.execute(query_delete_morning)
                self._cursor.execute(query_delete_afternoon)

            elif table == self._table_name_morning:
                self._cursor.execute(query_delete_morning)

            elif table == self._table_name_afternoon:
                self._cursor.execute(query_delete_afternoon)

        except sql.Error as e:
            print(e)
        else:
            self._connection.commit()

    def table_to_sql(self, table):
        if os.path.exists(f'Backup_DataBase/Backup_{table}.csv'):
            registereds = pd.read_csv(f'Backup_DataBase/Backup_{table}.csv', engine='c')
            registereds.to_sql(table, con=self._connection, if_exists='replace', index=False)
        else:
            print(f'Não existe backup da tabela {table}!')

    def import_backup_tables_presents(self, table='*'):
        if table == '*':
            self.table_to_sql(table=self._table_name_morning)
            self.table_to_sql(table=self._table_name_afternoon)
        elif table == self._table_name_morning:
            self.table_to_sql(table=self._table_name_morning)
        elif table == self._table_name_afternoon:
            self.table_to_sql(table=self._table_name_afternoon)

from DB import DataBase
import sqlite3 as sql
import pandas as pd
import os
import stat


class TableRegistered(DataBase):
    def __init__(self, check_same_thread=False):
        super().__init__(check_same_thread)
        self._cursor = self.get_cursor()
        self._connection = self.get_connection()
        self._table_name = 'Cadastrados'

        self._create_table_cadastrados()

    def _create_table_cadastrados(self):
        try:
            self._cursor.execute(f"""
                create table if not exists {self._table_name}
                (
                ID INTEGER not null constraint ID primary key autoincrement,
                email TEXT not null,
                NomeCompleto TEXT not null constraint Cadastrados_nomecompleto unique,
                Turma TEXT not null,
                Idade INTEGER not null,
                DiaCadastro TEXT not null,
                PeriodoEscolar TEXT not null,
                UNIQUE(email, NomeCompleto)
                )
                """)
        except sql.Error as err:
            print(err)
        else:
            self._connection.commit()

    def insert(self, email=None, name=None, _class=None, years=None, date=None, period=None):
        try:
            self._cursor.execute(f"""
            INSERT INTO {self._table_name} (email, NomeCompleto, Turma, Idade, DiaCadastro, 'PeriodoEscolar')
                        VALUES
                        (?, ?, ?, ?, ?, ?)
            """, (str(email), '_'.join(name.upper().split()), str(_class), int(years), str(date), str(period).upper()))
        except sql.Error as err:
            print(err)
            return False
        else:
            self._connection.commit()
            print('Armazenado com sucesso!!')
            return True

    def read_by_NomeCompleto(self, name):
        self._cursor.execute(f"""
        select * from {self._table_name} where NomeCompleto = ?;
        """, (name,))
        return self._cursor.fetchall()

    def read(self):
        self._cursor.execute(f"""select * from {self._table_name};""")
        return list(self._cursor.fetchall())

    def read_especified_column(self, column='*'):
        self._cursor.execute(f"""select {column} from {self._table_name}""")
        list_set_rows = set()
        for row in self._cursor.fetchall():
            list_set_rows.add(''.join(row))
        return list_set_rows

    def export_table_to_csv(self):
        try:
            path = f'Backup_DataBase/Backup_{self._table_name}.csv'
            if os.path.exists(path):
                os.remove(path)
            registereds = pd.read_sql(f'SELECT * FROM {self._table_name}', self._connection)
            registereds.to_csv(path, index=False)
            os.chmod(path, stat.S_IREAD)
        except Exception as err:
            print(err)
            print(f'Erro na exportação da tabela {self._table_name}!')

    def delete_all_data_from_cadastrados(self):
        try:
            query = f'delete from {self._table_name};'
            self._cursor.execute(query)
        except sql.Error as e:
            print(e)
        else:
            self._connection.commit()

    def import_backup_table_cadastrados(self):
        if os.path.exists(f'Backup_DataBase/Backup_{self._table_name}.csv'):

            registereds = pd.read_csv(f'Backup_DataBase/Backup_{self._table_name}.csv', engine='c')
            registereds.to_sql(self._table_name, con=self._connection, if_exists='replace', index=False)
        else:
            print(f'Não existe backup da tabela {self._table_name}!')

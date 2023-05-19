import time
from dash import Dash, html, Input, Output, ctx, dash_table, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import os
import signal


class Relatory:
    exit_now = False

    def __init__(self, table_presents, table_missings, table_registered):
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        self._info_student = None
        self._df_presents, self._df_missings, self._df_registered = None, None, None

        self._table_presents = table_presents
        self._table_missings = table_missings
        self._table_registered = table_registered

        self._cursor = self._table_registered.get_cursor()
        self._connection = self._table_registered.get_connection()
        self._cooldown = 0.1

        self._app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], update_title=None, title='Relatórios')

    def _exit_gracefully(self):
        self.exit_now = True

    def _set_info_students(self, info_student):
        self._info_student = {
            'id': info_student[0][0],
            'email': info_student[0][1],
            'name': info_student[0][2],
            'class': info_student[0][3],
            'years_old': info_student[0][4],
            'registered in': info_student[0][5],
            'period': info_student[0][-1]
        }

    def _run(self, debug):
        import webbrowser

        url = 'http://127.0.0.1:8080/'
        webbrowser.open(url)
        self._app.run(debug=debug, port=8080, use_reloader=False)

    def _datatable_presents(self):
        try:
            df_morning_presents = pd.read_sql('select * from PresentesManha', self._connection)
            df_afternoon_presents = pd.read_sql('select * from PresentesTarde', self._connection)
        except Exception as e:
            print(e)
            self._df_presents = pd.DataFrame()
            pass
        else:
            self._df_presents = pd.concat([df_morning_presents, df_afternoon_presents])
            self._df_presents.drop(columns=['Unnamed: 0'], errors='ignore', inplace=True)

    def _datatable_missings(self):
        try:
            df_morning_missings = pd.read_sql('select * from FaltantesManha', self._connection)
            df_afternoon_missings = pd.read_sql('select * from FaltantesTarde', self._connection)
        except Exception:
            self._df_missings = pd.DataFrame()
        else:
            self._df_missings = pd.concat([df_morning_missings, df_afternoon_missings])
            self._df_missings.drop(columns=['Unnamed: 0'], errors='ignore', inplace=True)

    def _datatable_registered(self):
        try:
            self._df_registered = pd.read_sql('select * from Cadastrados', con=self._connection)
            self._df_registered.drop(columns=['Unnamed: 0'], errors='ignore', inplace=True)
        except Exception:
            self._df_registered = pd.DataFrame()
            pass

    def _callbacks(self):
        @self._app.callback(
            Output('output-div-1', 'children'),
            Input('btn-exit-server', 'n_clicks')
        )
        def stop_program(n_clicks):
            if 'btn-exit-server' == ctx.triggered_id:
                try:
                    self._exit_gracefully()
                    return dbc.Alert(['Servidor fechado com sucesso! Pode fechar a página!'], id='stop-server',
                                     color='info', fade=True, dismissable=True, is_open=True,
                                     style={'alignText': 'center', 'marginTop': '1.5%'}), ''.format(
                        os.system('kill {}'.format(os.getpid()))).replace('', '')
                except Exception as e:
                    print(e)

        @self._app.callback(
            Output('download-cadastrados-csv', 'data'),
            Input('export-csv-cadastrados', 'n_clicks'),
            Input('table-cadastrados', 'data')
        )
        def export_table_registered_to_csv(n_clicks, data):
            if 'export-csv-cadastrados' == ctx.triggered_id:
                df = pd.DataFrame(data)
                return dcc.send_data_frame(df.to_csv, "Cadastrados_exported.csv")

        @self._app.callback(
            Output('download-faltas-csv', 'data'),
            Input('export-csv-faltas', 'n_clicks'),
            Input('table-faltantes', 'data')
        )
        def export_table_missings_to_csv(n_clicks, data):
            if 'export-csv-faltas' == ctx.triggered_id:
                df = pd.DataFrame(data)
                return dcc.send_data_frame(df.to_csv, "Faltantes_exported.csv")

        @self._app.callback(
            Output('download-presenca-csv', 'data'),
            Input('export-csv-presenca', 'n_clicks'),
            Input('table-presenca', 'data')
        )
        def export_table_presents_to_csv(n_clicks, data):
            if 'export-csv-presenca' == ctx.triggered_id:
                df = pd.DataFrame(data)
                return dcc.send_data_frame(df.to_csv, "Presenca_exported.csv")

        @self._app.callback(
            Output('output-row', 'children'),
            Input('search', 'n_clicks'),
            Input('query-aluno', 'value')
        )
        def set_student_info_from_search_bar(n_clicks, name):
            if 'search' == ctx.triggered_id and name is not None:
                name = '_'.join(name.upper().split())
                info_student = self._table_registered.read_by_NomeCompleto(name)
                self._set_info_students(info_student=info_student)
                return ''

        @self._app.callback(
            Output('num-presenca', 'children'),
            Output('num-presenca', 'hidden'),
            Input('search', 'n_clicks'),
            Input('query-aluno', 'value')
        )
        def number_of_presents(n_clicks, name):
            if 'search' == ctx.triggered_id and name is not None:
                time.sleep(self._cooldown)
                qty = 0
                if not self._df_presents.empty:
                    qty = len(self._df_presents.loc[self._df_presents['Aluno_ID'] == str(self._info_student['id'])])
                return 'Presenças: {}'.format(qty), False
            else:
                return 'Presenças: 0', False

        @self._app.callback(
            Output('num-faltas', 'children'),
            Output('num-faltas', 'hidden'),
            Input('search', 'n_clicks'),
            Input('query-aluno', 'value')
        )
        def number_of_missings(n_clicks, name):
            if 'search' == ctx.triggered_id and name is not None:
                time.sleep(self._cooldown)
                qty = 0
                if not self._df_missings.empty:
                    qty = len(self._df_missings.loc[self._df_missings['Aluno_ID'] == str(self._info_student['id'])])
                return 'Faltas: {}'.format(qty), False
            else:
                return 'Faltas: 0', False

        @self._app.callback(
            Output('idade', 'children'),
            Output('idade', 'hidden'),
            Input('search', 'n_clicks'),
            Input('query-aluno', 'value')
        )
        def years_old(n_clicks, name):
            if 'search' == ctx.triggered_id and name is not None:
                time.sleep(self._cooldown)
                return 'Idade: {}'.format(self._info_student['years_old']), False
            else:
                return 'Idade: xxx', False

        @self._app.callback(
            Output('turma', 'children'),
            Output('turma', 'hidden'),
            Input('search', 'n_clicks'),
            Input('query-aluno', 'value')
        )
        def class_(n_clicks, name):
            if 'search' == ctx.triggered_id and name is not None:
                time.sleep(self._cooldown)
                return 'Turma: {}'.format(self._info_student['class']), False
            else:
                return 'Turma: xxx', False

        @self._app.callback(
            Output('nome-aluno', 'children'),
            Output('nome-aluno', 'hidden'),
            Input('search', 'n_clicks'),
            Input('query-aluno', 'value')
        )
        def name(n_clicks, name):
            if 'search' == ctx.triggered_id and name is not None:
                time.sleep(self._cooldown)
                return f'Nome: {name}', False
            else:
                return 'Nome: ???', False

        @self._app.callback(
            Output('email-aluno', 'children'),
            Output('email-aluno', 'hidden'),
            Input('search', 'n_clicks'),
            Input('query-aluno', 'value')
        )
        def email(n_clicks, name):
            if 'search' == ctx.triggered_id and name is not None:
                time.sleep(self._cooldown)
                return f'Email: {self._info_student["email"]}', False
            else:
                return f'Email: xxx', False

        @self._app.callback(
            Output('dia-cadastro', 'children'),
            Output('dia-cadastro', 'hidden'),
            Input('search', 'n_clicks'),
            Input('query-aluno', 'value')
        )
        def dia_cadastro(n_clicks, name):
            if 'search' == ctx.triggered_id and name is not None:
                time.sleep(self._cooldown)
                return f'Cadastrado em: {self._info_student["registered in"]}', False
            else:
                return 'Cadastrado em: xxx', False

        @self._app.callback(
            Output('periodo', 'children'),
            Output('periodo', 'hidden'),
            Input('search', 'n_clicks'),
            Input('query-aluno', 'value')
        )
        def period(n_clicks, name):
            if 'search' == ctx.triggered_id and name is not None:
                time.sleep(self._cooldown)
                return f'Período: {self._info_student["period"]}', False
            else:
                return 'Período: xxx', False

        @self._app.callback(
            Output('id-aluno', 'children'),
            Output('id-aluno', 'hidden'),
            Input('search', 'n_clicks'),
            Input('query-aluno', 'value')
        )
        def id_aluno(n_clicks, name):
            if 'search' == ctx.triggered_id and name is not None:
                time.sleep(self._cooldown)
                return f'ID: {self._info_student["id"]}', False
            else:
                return 'ID: x', False

    def _layout(self):
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.InputGroup([
                                    dbc.InputGroupText('Nome do Aluno:'),
                                    dbc.Input(id='query-aluno')
                                ]),
                                dbc.Button('Buscar Aluno', id='search',
                                           style={'marginTop': '1.5%', 'marginBottom': '1.5%'})
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.H2(hidden=True, id='nome-aluno'),
                                ]),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.H2(hidden=True, id='id-aluno'),
                                ]),
                                dbc.Col([
                                    html.H2(hidden=True, id='email-aluno'),
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.H2(hidden=True, id='num-presenca'),
                                ]),
                                dbc.Col([
                                    html.H2(hidden=True, id='idade'),
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.H2(hidden=True, id='num-faltas'),
                                ]),
                                dbc.Col([
                                    html.H2(hidden=True, id='turma'),
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.H2(hidden=True, id='dia-cadastro'),
                                ]),
                                dbc.Col([
                                    html.H2(hidden=True, id='periodo'),
                                ])
                            ]),
                            dbc.Row(id='output-row'),
                            html.Hr(),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Fechar conexão com Servidor', id='btn-exit-server',
                                               style={'marginTop': '3.5%', 'marginLeft': '40%'}),
                                    html.Div(id='output-div-1')
                                ])
                            ])
                        ])
                    ], outline=True, color='secondary')
                ])
            ], style={'marginTop': '5%', 'marginBottom': '5%'}),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dash_table.DataTable(
                                        self._df_presents.to_dict('records'),
                                        [{'name': ['Presença', i], 'id': i} for i in self._df_presents.columns],
                                        merge_duplicate_headers=True,
                                        style_cell_conditional=[{'textAlign': 'center'}],
                                        style_as_list_view=True,
                                        page_size=5,
                                        page_current=0,
                                        page_action='native',
                                        filter_action="native",
                                        sort_action="native",
                                        sort_mode="multi",
                                        row_deletable=True,
                                        id='table-presenca'
                                    )
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Exportar para CSV', id='export-csv-presenca',
                                               style={'marginLeft': '45%'}),
                                    dcc.Download(id='download-presenca-csv')
                                ])
                            ], style={'marginTop': '3.5%'})
                        ])
                    ], outline=True, color='secondary')
                ], style={'marginBottom': '5%'}),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dash_table.DataTable(
                                        self._df_missings.to_dict('records'),
                                        [{'name': ['Faltas', i], 'id': i} for i in self._df_missings.columns],
                                        merge_duplicate_headers=True,
                                        style_cell_conditional=[{'textAlign': 'center'}],
                                        style_as_list_view=True,
                                        page_size=5,
                                        page_current=0,
                                        page_action='native',
                                        filter_action="native",
                                        sort_action="native",
                                        sort_mode="multi",
                                        row_deletable=True,
                                        id='table-faltantes'
                                    )
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Exportar para CSV', id='export-csv-faltas',
                                               style={'marginLeft': '45%'}),
                                    dcc.Download(id='download-faltas-csv')
                                ])
                            ], style={'marginTop': '3.5%'})
                        ])
                    ], outline=True, color='secondary')
                ])
            ], style={'marginTop': '5%', 'marginBottom': '5%'}),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dash_table.DataTable(
                                        self._df_registered.to_dict('records'),
                                        [{'name': ['Cadastrados', i], 'id': i} for i in self._df_registered.columns],
                                        merge_duplicate_headers=True,
                                        style_cell_conditional=[{'textAlign': 'center'}],
                                        style_as_list_view=True,
                                        page_size=5,
                                        page_current=0,
                                        page_action='native',
                                        filter_action="native",
                                        sort_action="native",
                                        sort_mode="multi",
                                        row_deletable=True,
                                        id='table-cadastrados'
                                    )
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Exportar para CSV', id='export-csv-cadastrados',
                                               style={'marginTop': '3.5%', 'marginLeft': '45%'}),
                                    dcc.Download(id='download-cadastrados-csv')
                                ])
                            ])
                        ])
                    ], outline=True, color='dark')
                ])
            ], style={'marginBottom': '2%'})
        ])

    def main(self, debug=False):
        self._datatable_registered()
        self._datatable_missings()
        self._datatable_presents()

        layout = self._layout()

        self._app.layout = layout
        self._callbacks()

        try:
            self._run(debug=debug)
        except Exception as err:
            print(err)
            print('\nServidor desligado com sucesso!\n')

from dash import Dash, html, Input, Output, ctx
from datetime import datetime
import dash_bootstrap_components as dbc
import os
import re
import signal


class Formulary:
    exit_now = False

    def __init__(self):
        signal.signal(signal.SIGTERM, self._exit_gracefully)
        self.pattern_name = '^[A-Z]+[a-z]+[A-Za-z\s]+$'
        self.pattern_email = '[a-z]+[a-z0-9]*(@)[a-z]+(.com)$'
        self.pattern_period = '(manhã|tarde|Manhã|Tarde)'
        self.ctrl = 0
        self._app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], update_title=None, title='Fomulário')

    def _exit_gracefully(self):
        self.exit_now = True

    def _run(self, debug=False):
        import webbrowser

        url = 'http://127.0.0.1:8050/'
        webbrowser.open(url)
        self._app.run(debug=debug, port=8050, use_reloader=False)

    def main(self, table_registered, debug=False):
        form = dbc.Container([
            dbc.Row([
                dbc.Card([
                    dbc.CardHeader(
                        [html.H2('Registre aluno para validação do reconhecimento facial!', className='card-title',
                                 style={
                                     'marginLeft': '20px',
                                     'marginTop': '25px',
                                     'marginBottom': '25px',
                                     'textAlign': 'center'
                                 })]),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.FormFloating([
                                        dbc.Input(pattern=self.pattern_name, id='name', placeholder='name'),
                                        dbc.Label('Nome Completo do Aluno')
                                    ])
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.FormFloating([
                                        dbc.Input(type="email", pattern=self.pattern_email, id='email',
                                                  placeholder='example@internet.com'),
                                        dbc.Label('Email')
                                    ])
                                ], style={'margin': '25px'})
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.FormFloating([
                                        dbc.Input(type="text", id='class', maxlength=15, placeholder='class'),
                                        dbc.Label('Turma')
                                    ])
                                ], style={'margin': '25px'}),
                                dbc.Col([
                                    dbc.FormFloating([
                                        dbc.Input(type='number', id='years', min=2, max=22, placeholder='years-old'),
                                        dbc.Label('Idade')
                                    ])
                                ], style={'margin': '25px'}),
                                dbc.Col([
                                    dbc.FormFloating([
                                        dbc.Input(type='text', id='period', pattern=self.pattern_period,
                                                  placeholder='period'),
                                        dbc.Label('Período (Manhã/Tarde)')
                                    ])
                                ], style={'margin': '25px'})
                            ]),
                            dbc.Row([

                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button('Enviar informações', id='btn', color='primary',
                                               class_name='mx-auto')
                                ], style={
                                    'width': '50%',
                                    'marginTop': '25px',
                                    'align': 'center'
                                }, class_name='mx-auto'),
                                dbc.Col([
                                    dbc.Button('Fechar conexão com servidor', id='btn-exit-server', color='primary',
                                               class_name='mx-auto')
                                ], style={
                                    'width': '50%',
                                    'marginTop': '25px',
                                    'align': 'center'
                                }, class_name='mx-auto')
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.P(id='output-text'),
                                    html.Div(id='output'),
                                    html.Div(id='output2')
                                ])
                            ])
                        ])
                    ]),
                ], style={'width': '75%', 'margin': '15%'}),
            ])
        ])
        self._app.layout = form

        @self._app.callback(
            Output('period', 'valid'),
            Input('period', 'value'),
            Input('period', 'pattern'),
        )
        def validate_period(value, padrao):
            if not bool(re.match(padrao, str(value))) or (len(value) == 0):
                return False
            if bool(re.match(padrao, value)):
                return True

        @self._app.callback(
            Output('name', 'valid'),
            Input('name', 'value'),
            Input('name', 'pattern'),
        )
        def validate_name(value, padrao):
            if not bool(re.match(padrao, str(value))) or (len(value) == 0):
                return False
            if bool(re.match(padrao, value)):
                return True

        @self._app.callback(
            Output('output2', 'children'),
            Input('btn-exit-server', 'n_clicks')
        )
        def stop_program(n_clicks):
            if 'btn-exit-server' == ctx.triggered_id:
                try:
                    self._exit_gracefully()
                    return dbc.Alert(['Servidor fechado com sucesso! Pode fechar a página!'], id='stop-server',
                                     color='info',
                                     is_open=True, fade=True, dismissable=True,
                                     style={'alignText': 'center'}), ''.format(
                        os.system('kill {}'.format(os.getpid()))).replace('0', '')
                except Exception as e:
                    print(e)

        @self._app.callback(
            Output('email', 'valid'),
            Input('email', 'value'),
            Input('email', 'pattern')
        )
        def validate_email(value, padrao):
            if not bool(re.match(padrao, str(value))):
                return False
            else:
                return True

        @self._app.callback(
            Output('output', 'children'),
            Input('name', 'value'),
            Input('name', 'valid'),
            Input('email', 'valid'),
            Input('period', 'valid'),
            Input('email', 'value'),
            Input('class', 'value'),
            Input('years', 'value'),
            Input('period', 'value'),
            Input('btn', 'n_clicks')
        )
        def get_validation(name_value, name_valid, email_valid, period_valid, email_value, class_value,
                           years_value, period_value, n_clicks):
            if years_value and class_value and email_valid and name_valid and period_valid:
                if 'btn' == ctx.triggered_id and self.ctrl == 0:
                    if table_registered.insert(email_value, name_value, class_value, years_value,
                                               datetime.now().strftime('%d/%m/%Y %H:%M:%S'), period_value):
                        self.ctrl += 1
                        return dbc.Alert(['Informações armazenadas com sucesso!'], id='alert-sucess', duration=2500,
                                         is_open=True, fade=True)
                    else:
                        return dbc.Alert(['Dados já existentes!'], color='danger', id='alert-fail', duration=2500,
                                         is_open=True, fade=True)
                elif 'btn' == ctx.triggered_id and self.ctrl != 0:
                    self.ctrl = 0
                    return dbc.Alert(['Informações já armazenadas!'], id='alert-already-sucess', color='warning',
                                     duration=2500, is_open=True, fade=True)
            else:
                pass

        try:
            self._run(debug=debug)
        except OSError:
            print('Página indisponível! Reinicie o programa para acessar a página!')
        except Exception as err:
            print(err)
            print('\nServidor desligado com sucesso!\n')
            return False

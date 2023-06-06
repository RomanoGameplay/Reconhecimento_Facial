from Schedules import Schedules
from DB import DataBase
from TableMissings import TableMissings
from TableRegistered import TableRegistered
from TablePresents import TablePresents
from settings import Settings
from datetime import datetime
from GetImages import GetImagesFromGmail
from Images import Images
from Formulary import Formulary
from FacialRecognition import FacialRecognition
from Relatory import Relatory
import os.path
import requests


class InterfaceMain:
    def __init__(self):
        self.table_missings = None
        self.table_registered = None
        self.table_presents = None
        self._key_exit = 'x'

    def _check_internet(self):

        url = 'https://www.google.com'
        timeout = 5
        try:
            requests.get(url, timeout=timeout)
        except requests.exceptions.ConnectionError:
            print('\nSem conexão com a internet!\n')
            return False
        else:
            print('\nConectado com a internet!\n')
            return True

    def _close_database(self):
        DataBase().close()

    @staticmethod
    def _title():
        print('=' * 45)
        print('LISTA DE PRESENÇA AUTOMATIZADA')
        print('=' * 45)

    def _backup_database(self):
        self.table_registered.export_table_to_csv()

        self.table_presents.export_table_to_csv('PresentesManha')
        self.table_presents.export_table_to_csv('PresentesTarde')

        self.table_missings.export_table_to_csv('FaltantesManha')
        self.table_missings.export_table_to_csv('FaltantesTarde')

        print('\nBackup criado na pasta "Backup_DataBase"!\n')

    def _import_backup_database(self):
        self.table_registered.import_backup_table_cadastrados()
        self.table_presents.import_backup_tables_presents()
        self.table_missings.import_backup_tables_missings()
        print('\nImportação do backup concluída!\n')

    def _delete_database(self):
        self.table_registered.delete_all_data_from_cadastrados()
        self.table_presents.delete_all_data()
        self.table_missings.delete_all_data()
        print('\nOs dados foram removidos com sucesso!\n')

    def _only2options(self, settings, schedules):
        while True:
            self._title()
            print('\nDefina as configurações, horários e aulas para ter acesso a outras opções:\n')
            print('1 - Definir horários!')
            print('2 - Definir configurações!')
            print('"{}" - sair!'.format(self._key_exit))

            input_option = input('\nEscolha uma das opções: ')
            if input_option == '1':
                schedules.main()
                continue
            elif input_option == '2':
                settings.main()
                continue
            elif input_option == self._key_exit:
                break
            else:
                print('Deve escolher apenas a opção com o número correspondente!')
                continue

    def _options(self, settings, schedules):
        try:
            obs = '   |__ OBS: Uma vez fechada a página, necessita-se de reiniciar o programa para acessá-la novamente!'
            configurations = settings.load_settings()
            images = Images(path=configurations['path'])
            schedules_data = schedules.load()
            morning_hours = schedules_data['horario_manha']
            afternoon_hours = schedules_data['horario_tarde']
            morning_hours = [datetime.strptime(morning_hours[0], '%H:%M'), datetime.strptime(morning_hours[1], '%H:%M')]
            afternoon_hours = [datetime.strptime(afternoon_hours[0], '%H:%M'),
                               datetime.strptime(afternoon_hours[1], '%H:%M')]

            while True:
                self._title()
                print('1 - Reconhecimento Facial! (Aperte "esc" para sair do reconhecimento facial!)')
                print('2 - Cadastrar alunos! (Requer conexão com a internet)\n', obs)
                print('3 - Baixar imagens do Gmail! (Requer conexão com a internet)')
                print('4 - Deletar imagens na pasta {}!'.format(configurations['path']))
                print('5 - Relatórios dos alunos! (Requer conexão com internet)\n', obs)
                print('6 - Alterar configurações!')
                print('7 - Alterar horários!')
                print('8 - Importar backups salvos do Banco de Dados!')
                print('9 - Deletar os dados do Banco de Dados!')
                print('"{}" - Sair!'.format(self._key_exit))

                input_option = input('\nDigite uma das opções acima: ')

                if input_option == '1':
                    facial_recognition = FacialRecognition(path=configurations['path'], morning_hours=morning_hours,
                                                           afternoon_hours=afternoon_hours)
                    facial_recognition.run(table_missings=self.table_missings, table_presents=self.table_presents,
                                           table_registered=self.table_registered)
                    if not os.path.exists('Backup_DataBase'):
                        os.makedirs('Backup_DataBase')
                    self._backup_database()
                    break
                elif input_option == '2':
                    if self._check_internet():
                        web_formulary = Formulary()
                        web_formulary.main(self.table_registered, debug=False)
                        continue
                    continue
                elif input_option == '3':
                    if self._check_internet():
                        gmail = GetImagesFromGmail(user=configurations['email_user_gmail'],
                                                   subject=configurations['subject_gmail'], path=configurations['path'],
                                                   gmail_access=configurations['gmail_access'])
                        gmail.main(self.table_registered)
                        images.resize_images()
                        continue
                    continue
                elif input_option == '4':
                    images.delete_all_images()
                    continue
                elif input_option == '5':
                    if self._check_internet():
                        web_relatory = Relatory(table_presents=self.table_presents, table_registered=self.table_registered,
                                                table_missings=self.table_missings)
                        web_relatory.main(debug=False)
                        continue
                    continue
                elif input_option == '6':
                    settings.main()
                    continue
                elif input_option == '7':
                    schedules.main()
                    continue
                elif input_option == '8':
                    self._import_backup_database()
                    continue
                elif input_option == '9':
                    delete_data = input(
                        'Você tem certeza?\nEssa ação apagará todos os dados existentes nso bancos de dados!zn\t[S | N]: ')
                    if delete_data.upper() == 'S':
                        self._delete_database()
                        print('\nDados apagados!\n')
                    continue
                elif input_option == self._key_exit:
                    break
                else:
                    print('\nEscolha apenas a opção com o número correspondente!\n')
                    continue
        except KeyboardInterrupt:
            print('Programa parado de forma forçada!')
        except Exception as e:
            print(e)

    def main(self):
        try:
            settings = Settings()
            schedules = Schedules()

            if os.path.isfile(settings.json_filename) and os.path.isfile(schedules.json_filename):
                self.table_missings = TableMissings()
                self.table_registered = TableRegistered()
                self.table_presents = TablePresents()
                self._options(settings=settings, schedules=schedules)
                self._close_database()
            else:
                self._only2options(settings=settings, schedules=schedules)
                print('\nNovas opções disponíveis quando reiniciar o programa!')

        except Exception as e:
            print(e)
        else:
            print('\nFIM DO PROGRAMA!')



if __name__ == '__main__':
    interface = InterfaceMain()
    interface.main()

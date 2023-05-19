import re
import json
import os


class Settings:
    def __init__(self):
        self.key_exit = 'x'
        self.config = {
            'path': None,
            'email_user_gmail': None,
            'subject_gmail': None,
            'gmail_access': None
        }
        self.json_filename = 'configurations.json'
        try:
            if os.path.isfile(self.json_filename) and os.access(self.json_filename, os.R_OK):
                self.config = self.load_settings()
        except FileNotFoundError or FileExistsError:
            self.save_settings()

    def set_path(self, path): self.config['path'] = path

    def set_gmail_acess(self, gmail_access): self.config['gmail_access'] = gmail_access

    def set_subject_gmail(self, subject_gmail): self.config['subject_gmail'] = subject_gmail

    def set_email_user_gmail(self, email_user_gmail):
        if re.match("^[a-z0-9]+(@)[a-z]+(.com)$", email_user_gmail):
            self.config['email_user_gmail'] = email_user_gmail
            print('formato de email aceito!')
        else:
            print('\nSua entrada não está no formato esperado!\nDigite novamente!')

    def save_settings(self):
        try:
            save_file = open(self.json_filename, 'w')
            json.dump(self.config, save_file)
        except:
            print('Erro ao salvar arquivo "{}"!'.format(self.json_filename))

    def load_settings(self):
        try:
            load_file = open(self.json_filename,)
            data = json.load(load_file)
            self.config = {
                'path': data['path'],
                'email_user_gmail': data['email_user_gmail'],
                'subject_gmail': data['subject_gmail'],
                'gmail_access': data['gmail_access']
            }
        except:
            print('Erro ao carregar arquivo "{}"!'.format(self.json_filename))
        else:
            return self.config

    def show_config(self):
        print('\n')
        for k, v in self.config.items():
            print('{} - {}'.format(k, v))

    @staticmethod
    def title():
        print('=' * 45)
        print('CONFIGURAÇÕES GERAIS')
        print('=' * 45)

    def options(self):
        self.title()
        print(
            '\nDeseja alterar alguma configuração?\nDigite "{}" para o término das alterações!\n'.format(self.key_exit))
        print('1 (path) Inserir nome da pasta onde serão armazenadas as imagens!')
        print('2  -(email) Inserir email para receber as imagens do Gmail!')
        print(
            '3 - (subject) Inserir o subject (título) que o programa deve reconhecer\n '
            'nas mensagens do gmail ao fazer a detecção e download das imagens do gmail')
        print('4 - Inserir senha de acesso ao gmail!')
        print('5 - Salvar configurações!')
        print('6 - Carregar configurações!')
        print('7 - Mostrar as configurações!')
        print('{} - Para sair do programa!'.format(self.key_exit))

    def main(self):
        try:
            while True:
                self.options()
                res = input('\nDigite um dos números acima: ')
                if res == '1':
                    self.set_path(input('digite o nome da pasta: '))
                elif res == '2':
                    self.set_email_user_gmail(input('Digite seu email: '))
                elif res == '3':
                    self.set_subject_gmail(input('Digite o subject(título) que o programa deve reconhecer\n '
                                                 'nas mensagens do gmail para a detecção e download das imagens'))
                elif res == '4':
                    self.set_gmail_acess(input('Cole a senha de acesso para o gmail: '))
                elif res == '5':
                    self.save_settings()
                elif res == '6':
                    self.load_settings()
                    print('Configurações carregadas!')
                elif res == '7':
                    self.show_config()
                elif res == self.key_exit:
                    self.show_config()
                    break
                else:
                    print('\nvocê digitar apenas os números referenciados acima!')
        except KeyboardInterrupt:
            pass







# import re
# import json
# import os
#
#
# class Settings:
#     def __init__(self):
#         self._key_exit = 'x'
#         self._configurations = {
#             'path': None,
#             'email_user_gmail': None,
#             'subject_gmail': None
#         }
#         self.json_filename = 'configurations.json'
#         try:
#             if os.path.isfile(self.json_filename) and os.access(self.json_filename, os.R_OK):
#                 self._configurations = self.load()
#         except FileNotFoundError or FileExistsError:
#             self.save()
#
#     def set_path(self, path):
#         self._configurations['path'] = path
#
#     def set_subject_gmail(self, subject_gmail):
#         self._configurations['subject_gmail'] = subject_gmail
#
#     def set_email_user_gmail(self, email_user_gmail):
#         if re.match("^[a-z0-9]+(@)[a-z]+(.com)$", email_user_gmail):
#             self._configurations['email_user_gmail'] = email_user_gmail
#             print('formato de email aceito!')
#         else:
#             print('\nSua entrada não está no formato esperado!\nDigite novamente!')
#
#     def save(self):
#         try:
#             save_file = open(self.json_filename, 'w')
#             json.dump(self._configurations, save_file)
#         except Exception as err:
#             print(err)
#             print('\nErro ao salvar arquivo "{}"!\n'.format(self.json_filename))
#
#     def load(self):
#         try:
#             load_file = open(self.json_filename, )
#             data = json.load(load_file)
#             self._configurations = {
#                 'path': data['path'],
#                 'email_user_gmail': data['email_user_gmail'],
#                 'subject_gmail': data['subject_gmail']
#             }
#         except Exception as err:
#             print(err)
#             print('\nErro ao carregar arquivo "{}"!\n'.format(self.json_filename))
#         else:
#             return self._configurations
#
#     def show_configurations(self):
#         print('\n')
#         for k, v in self._configurations.items():
#             print('{} - {}'.format(k, v))
#
#     def options(self):
#         print('=' * 45)
#         print('CONFIGURAÇÕES GERAIS')
#         print('=' * 45)
#         print(
#             '\nDeseja alterar alguma configuração?\nDigite "{}" para o término das alterações!\n'.format(
#                 self._key_exit))
#         print('1 - (path) Inserir nome da pasta onde serão armazenadas as imagens!')
#         print('2 - (email) Inserir email para receber as imagens do Gmail!')
#         print(
#             '3 - (subject) Inserir o subject (título) que o programa deve reconhecer\n '
#             'nas mensagens do gmail ao fazer a detecção e download das imagens do gmail')
#         print('4 - Salvar configurações!')
#         print('5 - Carregar configurações!')
#         print('6 - Mostrar as configurações!')
#         print('{} - Para sair do programa!'.format(self._key_exit))
#
#     def main(self):
#         try:
#             while True:
#                 self.options()
#                 input_option = input('\nDigite um dos números acima: ')
#                 if input_option == '1':
#                     self.set_path(input('digite o nome da pasta: '))
#                 elif input_option == '2':
#                     self.set_email_user_gmail(input('Digite seu email: '))
#                 elif input_option == '3':
#                     self.set_subject_gmail(input('Digite o subject(título) que o programa deve reconhecer\n\t\t '
#                                                  'nas mensagens do gmail para a detecção e download das imagens: '))
#                 elif input_option == '4':
#                     self.save()
#                 elif input_option == '5':
#                     self.load()
#                     print('Configurações carregadas!')
#                 elif input_option == '6':
#                     self.show_configurations()
#                 elif input_option == self._key_exit:
#                     self.show_configurations()
#                     break
#                 else:
#                     print('\nvocê digitar apenas os números referenciados acima!\n')
#         except KeyboardInterrupt:
#             print('\n --> Programa abortado!\n\t\tAlterações não salvas!')
#
#
# if __name__ == '__main__':
#     Settings().main()

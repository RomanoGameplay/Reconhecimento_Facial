import json
import os
import re


class Schedules:
    def __init__(self):
        self.horario_manha = []
        self.horario_tarde = []
        self.key_exit = 'x'
        self.json_filename = 'schedules.json'
        self.pattern = '[0-9]{2}(:)[0-9]{2}'

        try:
            if os.path.isfile(self.json_filename) and os.access(self.json_filename, os.R_OK):
                self.horario_manha, self.horario_tarde = self.load()
        except FileNotFoundError or FileExistsError:
            self.save()

    def validate_hour(self, hour):
        if re.match(self.pattern, hour):
            return True
        else:
            return False

    def set_horario_manha(self):
        while True:
            horario_manha = []
            response = input('Digite o início e fim do horário da manhã, com o formato "HH:MM HH:MM": ').split()
            if len(response) == 0:
                print('Vocẽ deve digitar alguma coisa!')
            else:
                for i in response:
                    if bool(re.match(self.pattern, i)):
                        horario_manha.append(i)
                    else:
                        print('Formato de entrada incorreto ou incompleto!')
                        horario_manha.clear()

                if bool(re.match(self.pattern, response[0])) and bool(re.match(self.pattern, response[1])):
                    self.horario_manha = horario_manha
                    break

    def set_horario_tarde(self):
        while True:
            horario_tarde = []
            response = input('Digite o início e fim do horário da tarde, com o formato "HH:MM HH:MM": ').split()
            if len(response) == 0:
                print('Vocẽ deve digitar alguma coisa!')
            else:
                for i in response:
                    if bool(re.match(self.pattern, i)):
                        horario_tarde.append(i)
                    else:
                        print('Formato de entrada incorreto ou incompleto!')
                        horario_tarde.clear()

                if bool(re.match(self.pattern, response[0])) and bool(re.match(self.pattern, response[1])):
                    self.horario_tarde = horario_tarde
                    break

    def show_horario_manha(self):
        try:
            print('\nHorário da manhã = {} - {}\n'.format(self.horario_manha[0], self.horario_manha[1]))
        except Exception as e:
            print('\n<< Erro na função {}() >>'.format(self.show_horario_manha.__name__))
            print(f'\n{e}')

    def show_horario_tarde(self):
        try:
            print('\nHorário da tarde = {} - {}\n'.format(self.horario_tarde[0], self.horario_tarde[1]))
        except Exception as e:
            print('\n<< Erro na função {}() >>'.format(self.show_horario_tarde.__name__))
            print(f'\n{e}')

    def save(self):
        x = {
            'horario_manha': self.horario_manha,
            'horario_tarde': self.horario_tarde
        }
        save_file = open(self.json_filename, 'w')
        json.dump(x, save_file)
        print('\nConfigurações salvas com sucesso!\n')

    def load(self):
        with open(self.json_filename, encoding='utf-8') as schedules_data:
            data = json.load(schedules_data)
            self.horario_manha = data['horario_manha']
            self.horario_tarde = data['horario_tarde']
            return data

    def title(self):
        print('=' * 45)
        print('CONFIGURAÇÕES DOS HORÁRIOS')
        print('=' * 45)

    def options(self):
        self.title()
        print('\nDigite a opção que deseja:')
        print('1 - Definir/alterar horário da manhã e da tarde')
        print('2 - Mostrar horários da manhã e da tarde')
        print('3 - Salvar configurações')
        print('4 - Carregar informações')
        print('{} - sair do programa!'.format(self.key_exit))

    def main(self):
        try:
            while True:
                self.options()
                response = input('\nDigite um dos números acima: ')

                if response == '1':
                    self.set_horario_manha()
                    self.set_horario_tarde()
                elif response == '2':
                    self.show_horario_manha()
                    self.show_horario_tarde()
                elif response == '3':
                    self.save()
                elif response == '4':
                    self.load()
                elif response == self.key_exit:
                    print('\n')
                    self.save()
                    break
                else:
                    print('Deve escolher apenas o número referente a cada opção!')
        except KeyboardInterrupt:
            pass

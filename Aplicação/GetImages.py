from imap_tools import MailBox, AND
import face_recognition as fr
import os
import re


class GetImagesFromGmail:
    def __init__(self, user, subject, path, gmail_access):
        try:
            self._user, self._subject, self._path = user, subject, path
            self._passwd = gmail_access
            self._pattern = "^[A-Za-z_.]*[.png|.jpg|.jpeg|.webp]$"
            self._connection_email = MailBox("imap.gmail.com").login(self._user, self._passwd)
        except Exception as err:
            print(err)
            print('\n**Conexão com o gmail fracassado!\n')
        else:
            print('Gmail conectado com sucesso! folder atual: ' + self._connection_email.folder.get() + '\n')

    def _detect_face_in_image(self, info, filename):
        try:
            with open('test_detect.bin', 'wb') as fb:
                fb.write(info)
                img = fr.load_image_file('test_detect.bin')
                os.remove('test_detect.bin')
                fr.face_locations(img)[0]
        except Exception as err:
            print(err)
            print('\n\t**Erro na detecção de rosto na foto {}\n'.format(filename))
            return False
        else:
            return True

    def _export_image_to_directory(self, filename, info):
        with open('{}/'.format(self._path) + filename, 'wb') as f:
            f.write(info)
            print()

    def main(self, table_registered):
        list_emails = table_registered.read_especified_column('email')
        list_names = table_registered.read_especified_column('NomeCompleto')
        number_emails_read = len(list_emails)
        number_images = 0
        try:
            ctrl = 1
            print('Iníciando análise!\n')
            for email in list_emails:
                print('emails verificados: {}/{}'.format(ctrl, number_emails_read))
                ctrl += 1
                for emails in self._connection_email.fetch(AND(from_=email, to=self._user)):
                    if len(emails.attachments) > 0:
                        if emails.subject == self._subject:
                            for anexo in emails.attachments:
                                if bool(re.match(self._pattern, anexo.filename)):
                                    info = anexo.payload
                                    print('Iniciando análise na imagem {}'.format(anexo.filename))
                                    number_images += 1
                                    if self._detect_face_in_image(info, anexo.filename):
                                        name = anexo.filename.upper().split('.')[0]
                                        if name in list_names:
                                            self._export_image_to_directory(anexo.filename, info)
                                            print('{} baixada com sucesso!'.format(anexo.filename))
        except KeyboardInterrupt:
            print('\nPrograma abortado pelo usuário!\n')
        except Exception as e:
            print(e)
            print('\nErro na função main() da classe GetImages!\n')
        else:
            print('\nFim da verificação!\nTotal de emails analisadas: {}\nTotal de fotos verificadas: {}\n'.format(
                number_emails_read, number_images))

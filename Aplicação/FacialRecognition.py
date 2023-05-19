from datetime import datetime
import sqlite3 as sql
import os
import face_recognition as fr
import cv2
import numpy as np


class FacialRecognition:
    def __init__(self, path, morning_hours, afternoon_hours):
        self.video_capture = cv2.VideoCapture(0)
        self.path = path
        self.images = []
        self.classNames = []
        self._morning_hours = morning_hours
        self._afternoon_hours = afternoon_hours

        self.mylist = os.listdir(self.path)
        for cl in self.mylist:
            curImg = cv2.imread(f'{self.path}/{cl}')
            self.images.append(curImg)
            self.classNames.append(os.path.splitext(cl)[0])
        self.encodeListKnown = self._find_encodings(self.images)

    def _insert_on_table_presents(self, name, table_presents, table_registered, names_in_table_registered, used_names):
        try:
            if name in names_in_table_registered and name not in used_names:
                result_query = table_registered.read_by_NomeCompleto(name.upper())
                date = datetime.now().strftime('%d/%m/%Y %H:%M:%S').split(' ')
                used_names.add(name)
                try:
                    if result_query[0][-1] == 'MANHÃ':
                        table_presents.insert(table='PresentesManha', aluno_id=result_query[0][0], date_present=date[0],
                                              hours=date[1])

                    elif result_query[0][-1] == 'TARDE':
                        table_presents.insert(table='PresentesTarde', aluno_id=result_query[0][0], date_present=date[0],
                                              hours=date[1])
                except sql.Error as err:
                    print(err)
        except sql.Error:
            pass
        except Exception as e:
            print('\nErro na inserção!\n')
            print(e)

    def _find_encodings(self, images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = fr.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    def run(self, table_missings, table_presents, table_registered):
        used_names = set()
        names_in_table_registered = table_registered.read_especified_column('NomeCompleto')
        process_this_frame = True

        while True:
            current_time = datetime.strptime(datetime.now().strftime('%H:%M'), '%H:%M')
            if self._morning_hours[0] <= current_time <= self._morning_hours[1]:
                table_missings.insert_data_into_table(table='PresentesManha', period='Manhã'.upper())
                print('\nFim do horário!')
                break
            elif self._afternoon_hours[0] <= current_time <= self._afternoon_hours[1]:
                table_missings.insert_data_into_table(table='FaltantesTarde', period='Tarde'.upper())
                print('\nFim do horário!')
                break

            ret, frame = self.video_capture.read()

            if process_this_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                rgb_small_frame = small_frame[:, :, ::-1]

                face_locations = fr.face_locations(rgb_small_frame)
                face_encodings = fr.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    matches = fr.compare_faces(self.encodeListKnown, face_encoding)
                    name = "Unknown"
                    color = (0, 0, 255)

                    face_distances = fr.face_distance(self.encodeListKnown, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.classNames[best_match_index]
                        color = (0, 255, 0)

                    face_names.append(name)

            process_this_frame = not process_this_frame

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left + 6, top - 6), cv2.FONT_HERSHEY_COMPLEX, 1.0, (255, 255, 255), 1)
                if name != 'Unknown':
                    name = name.upper()
                    self._insert_on_table_presents(name, table_presents, table_registered, names_in_table_registered,
                                                   used_names)
            cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        self.video_capture.release()
        cv2.destroyAllWindows()

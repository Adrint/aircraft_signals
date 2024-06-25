# -*- coding: utf-8 -*-
import pymongo
import datetime
import json
from bson import ObjectId
import codecs

# Klasa do serializacji obiektów ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

# Funkcja do konwersji czasu epoch na format czytelny dla człowieka
def convert_epoch_time(epoch_time):
    epoch_time = int(epoch_time)
    dt = datetime.datetime.fromtimestamp(epoch_time)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# Połączenie z bazą danych MongoDB
client = pymongo.MongoClient('mongodb://student:student@10.20.66.7/fsig-raw')
db = client['fsig-raw']
collection = db['rawFaSignals']

# Kryteria wyszukiwania początkowych dokumentów
initial_criteria = {
    "value.type": "flightplan"
}

# Znajdź wszystkie dokumenty spełniające początkowe kryteria
initial_documents = collection.find(initial_criteria)

# Pobranie liczby dokumentów do przetworzenia od użytkownika
while True:
    try:
        num_documents = int(input("Podaj liczbę dokumentów do przetworzenia: "))  # Użyj input w Pythonie 3
        if num_documents > 0:
            break
        else:
            print("Podaj liczbę większą od zera.")
    except ValueError:
        print("Podaj prawidłową liczbę całkowitą.")

# Przetwarzanie każdej pary ident i pitr
with codecs.open('ident_data.json', 'w', encoding='utf-8') as file:  # Użyj codecs.open do obsługi UTF-8
    for i, dokument in enumerate(initial_documents):
        if i >= num_documents:
            break

        dict_dokument = dict(dokument)
        dict_value = dict_dokument.get('value', {})

        ident = dict_value.get('ident', '')
        pitr = dict_value.get('pitr', '')


        if ident and pitr:
            # Kryteria wyszukiwania na podstawie ident i pitr
            criteria = {
                "$and": [
                    {"value.pitr": pitr},
                    {"value.type": "flightplan"},
                    {"value.ident": ident},
                ]
            }

            # Znajdź dokumenty na podstawie kryteriów
            documents = collection.find(criteria)

            # Przetwarzanie i zapisywanie dokumentów do pliku JSON
            for dokument in documents:
                dict_dokument = dict(dokument)
                dict_value = dict_dokument.get('value', {})

                # Sprawdzenie czy waypoints nie są puste i czy mają lon, lat, alt, clock
                waypoints = dict_value.get('waypoints', [])
                if not waypoints:
                    print("Dokument {} ma puste waypoints.".format(ident))
                    continue  # Pomijamy dokumenty bez waypoints
                if any('lon' not in wp or 'lat' not in wp for wp in waypoints):
                    print("Dokument {} ma niepełne dane w waypoints.".format(ident))
                    continue  # Pomijamy dokumenty bez właściwych waypoints

                # Konwersja znacznika czasu PITR
                if 'pitr' in dict_value:
                    dict_value['pitr'] = convert_epoch_time(dict_value['pitr'])

                # Przygotowanie danych do serializacji
                output = {
                    "ident": dict_value.get('ident', ''),
                    "reg": dict_value.get('reg', ''),
                    "pitr": dict_value.get('pitr', '')
                    #"waypoints": [{"lon": wp.get('lon'), "lat": wp.get('lat')} for wp in waypoints if 'lon' in wp and 'lat' in wp]
                }

                # Serializacja do JSON
                json_document = json.dumps(output, cls=JSONEncoder, ensure_ascii=False)
                file.write(json_document + '\n')

print("Zakończono zapisywanie danych do pliku.")

# Otwarcie pliku JSON i wypisanie jego zawartości na konsoli
with codecs.open('ident_data.json', 'r', encoding='utf-8') as file:  # Użyj codecs.open do obsługi UTF-8
    for line in file:
        line = line.strip()
        if line:
            print(line)



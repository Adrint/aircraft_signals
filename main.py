# -*- coding: utf-8 -*-
import pymongo
import datetime
import json
import codecs

# Klasa do serializacji obiektów ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pymongo.ObjectId):
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

# Kryteria wyszukiwania dokumentów dla ident "CSH9141"
criteria = {
    "value.type": "position",
    "value.reg": {"$exists": True, "$ne": ""},
}

while True:
    value_ident = raw_input("Podaj wartość ident (np. CSH9141): ")  # Użyj raw_input dla Pythona 2.7
    if value_ident.strip():
        criteria["value.ident"] = value_ident.strip()
        break
    else:
        print("Podaj prawidłową wartość ident.")

# Pobranie liczby dokumentów do przetworzenia od użytkownika
while True:
    try:
        num_documents = int(raw_input("Podaj liczbę dokumentów do przetworzenia: "))  # Użyj raw_input dla Pythona 2.7
        if num_documents > 0:
            break
        else:
            print("Podaj liczbę większą od zera.")
    except ValueError:
        print("Podaj prawidłową liczbę całkowitą.")

# Znajdź wszystkie dokumenty spełniające kryteria z limitem
documents = collection.find(criteria).limit(num_documents)

# Przetwarzanie i zapisywanie dokumentów do pliku JSON
with codecs.open('data.json', 'w', encoding='utf-8') as file:
    count = 0
    for dokument in documents:
        dict_dokument = dict(dokument)
        dict_value = dict_dokument.get('value', {})

        # Pobieranie danych z dokumentu
        ident = dict_value.get('ident', '')
        pitr = dict_value.get('pitr', '')
        air_ground = dict_value.get('air_ground', '')
        lat = dict_value.get('lat', '')
        lon = dict_value.get('lon', '')
        alt = dict_value.get('alt', '')
        clock = dict_value.get('clock', '')
        reg = dict_value.get('reg', '')

        # Konwersja czasu PITR
        if pitr:
            pitr = convert_epoch_time(pitr)

        if clock:
            clock = convert_epoch_time(clock)

        # Przygotowanie danych do zapisu
        output = {
            "ident": ident,
            "pitr": pitr,
            "air_ground": air_ground,
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "clock": clock,
            "reg": reg,
        }

        # Serializacja do JSON
        json_document = json.dumps(output, cls=JSONEncoder, ensure_ascii=False)
        file.write(json_document + '\n')

        count += 1
        if count >= num_documents:
            break

print("Zakończono zapisywanie {} dokumentów dla ident 'CSH9141' do pliku 'data.json'.".format(num_documents))

# Otwarcie pliku JSON i wypisanie jego zawartości na konsoli
with codecs.open('data.json', 'r', encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        if line:
            print(line)

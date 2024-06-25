import json
import os
from geopy.distance import great_circle
from shapely.geometry import LineString
from datetime import datetime

# Ścieżka do folderu z plikami JSON
input_folder_path = r'D:\aircraft_signals 2\dane\json\data'
output_folder_path = r'D:\aircraft_signals 2\dane\json\output'  # Nowa ścieżka do folderu wyjściowego

# Lista nazw plików do przetworzenia
files_to_process = ['AAL639.json','AAL1203.json','AAL1632.json', 'AAL2254.json', 'CBJ480.json', 'DAL446.json', 'DAL1155.json','JBU1197.json','KAL124.json','NKS957.json', 'QFA79.json', 'SWA622.json', 'THY1.json', 'UAL595.json', 'VOZ214.json']

# Utwórz folder wyjściowy, jeśli nie istnieje
os.makedirs(output_folder_path, exist_ok=True)

# Przetwarzanie każdego pliku
for filename in files_to_process:
    file_path = os.path.join(input_folder_path, filename)
    output_filename = f"output_{filename[:-5]}.json"  # Nazwa pliku wynikowego
    
    # Lista do przechowywania punktów
    waypoints = []

    # Wczytaj dane z pliku JSON
    with open(file_path, 'r') as file:
        for line in file:
            try:
                # Usuń niepotrzebne znaki nowej linii lub inne zbędne znaki
                cleaned_line = line.strip()

                # Parsuj linię jako obiekt JSON
                obj = json.loads(cleaned_line)

                # Pobierz potrzebne informacje
                ident = obj['ident']
                reg = obj['reg']
                lat = float(obj['lat'])  # Konwertuj na float
                lon = float(obj['lon'])  # Konwertuj na float
                
                # Sprawdź czy pole alt zawiera wartość
                if 'alt' in obj and obj['alt']:
                    alt = int(obj['alt'])  # Konwertuj na int
                else:
                    alt = -1  # Domyślna wartość, gdy alt jest puste lub nie istnieje
                
                clock = obj['clock']

                # Dodaj punkt do listy waypoints
                waypoints.append({"lat": lat, "lon": lon, "alt": alt, "clock": clock})

            except json.JSONDecodeError as e:
                print(f"Błąd podczas parsowania JSON w pliku {filename}, linia: {cleaned_line[:50]}...")
                print(f"Komunikat błędu: {str(e)}")
                continue

    # Utwórz docelowy obiekt JSON
    output_data = {
        "ident": ident,
        "reg": reg,
        "waypoints": waypoints
    }

    # Konwertuj output_data do formatu JSON
    output_json = json.dumps(output_data, indent=2)

    # Zapisz wynikowy JSON do pliku w folderze wyjściowym
    output_file = os.path.join(output_folder_path, output_filename)
    with open(output_file, 'w') as outfile:
        outfile.write(output_json)

    print(f"Dane zostały zapisane do pliku: {output_file}")


Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_AAL639.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_AAL1203.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_AAL1632.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_AAL2254.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_CBJ480.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_DAL446.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_DAL1155.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_JBU1197.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_KAL124.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_NKS957.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_QFA79.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_SWA622.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_THY1.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_UAL595.json
Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\output_VOZ214.json

folder_path = r'D:\aircraft_signals 2\dane\json\output'
output_folder_path2 = r'D:\aircraft_signals 2\dane\json\output'  # Nowa ścieżka do folderu wyjściowego
# Lista nazw plików do przetworzenia
files_to_process = ['output_AAL639.json','output_AAL1203.json','output_AAL1632.json','output_AAL2254.json','output_CBJ480.json','output_DAL446.json','output_DAL1155.json','output_JBU1197.json','output_KAL124.json','output_NKS957.json','output_QFA79.json','output_SWA622.json','output_THY1.json','output_UAL595.json','output_VOZ214.json']

# Lista do przechowywania danych wynikowych
merged_data = []

# Przetwarzanie każdego pliku
for filename in files_to_process:
    file_path = os.path.join(folder_path, filename)
    
    # Wczytaj dane z pliku JSON
    with open(file_path, 'r') as file:
        try:
            # Parsuj dane z pliku JSON
            data = json.load(file)
            
            # Dodaj dane do listy merged_data
            merged_data.append(data)
        
        except json.JSONDecodeError as e:
            print(f"Błąd podczas parsowania JSON w pliku {filename}: {str(e)}")
            continue

# Utwórz ścieżkę dla pliku wynikowego zbiorczego
output_path = os.path.join(output_folder_path2 , 'merged_output.json')

# Zapisz merged_data do pliku JSON
with open(output_path, 'w') as outfile:
    json.dump(merged_data, outfile, indent=2)

print(f"Dane zostały zapisane do pliku: {output_path}")

Dane zostały zapisane do pliku: D:\aircraft_signals 2\dane\json\output\merged_output.json


from flask import Flask, render_template  # importowanie flask do tworzenia aplikacji webowej oraz render_template do wyświetlania szablonów html
import os  # moduł systemowy do interakcji z systemem plików i zmiennymi środowiskowymi
import json  # moduł json do pracy z danymi w formacie json, odczyt i zapis danych 

# inicjalizacja instancji aplikacji Flask, __name__ określa nazwę bieżącego modułu - __main__ dla pliku głównego
app = Flask(__name__)  # tworzenie aplikacji webowej, __name__ określa nazwę bieżącego modułu (potrzebne dla flask)

# pobranie ścieżki do folderu z danymi ze zmiennej środowiskowej DATA_FOLDER (jeśli nie istnieje to ./data jako domyślne)
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")

# dekorator @app.route określa adres URL obsługiwany przez funkcje index
@app.route('/')
def index(): 
    try:
        # pobranie listy plików z folderu DATA_FOLDER
        files = os.listdir(DATA_FOLDER)
        
        # tworzenie pustej listy, do której będą dodawane dane z plików json
        measurements = []

        # iterowanie wszystkich plików w folderze
        for file in files:
            if file.endswith('.json'):  # sprawdzanie czy plik ma rozszerzenie .json
                file_path = os.path.join(DATA_FOLDER, file)  # tworzenie pełnej ścieżki do pliku, łącząc folder z nazwą pliku

                # otwieranie pliku json w trybie odczytu ('r'), dla bezpieczenstwa
                with open(file_path, 'r') as f:
                    data = json.load(f)  # wczytywanie zawartości pliku jako dane json, słownik
                    measurements.append({  # dodawanie do listy measurements słownika z nazwą pliku (file) i jego zawartością (data)
                        "file": file,  # przechowywanie nazwy pliku
                        "data": data  # przechowywanie zawartości pliku JSON
                    })

        # renderowanie szablonu html(index.html) i przekazanie listy measurements do wyświetlenia na stronie
        return render_template('index.html', measurements=measurements)

    # obsługabsługa błędów, jeśli folder nie istnieje lub plik json jest uszkodzony
    except Exception as e:
        return f"Error: {str(e)}"  # zwracanie komunikatu błędu w formie tekstowej, str(e) - zamienia wyjątek na czytelny ciąg znaków


# uruchomienie flaska
if __name__ == '__main__':  # czy plik jest uruchamiany bezpośrednio, a nie jako moduł
    app.run(host='0.0.0.0', port=5000)  # uruchomienie serwera na porcie 5000, dostępnego na wszystkich interfejsach sieciowych (host 0.0.0.0)

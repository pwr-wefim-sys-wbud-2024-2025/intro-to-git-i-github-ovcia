import requests
import os
from datetime import datetime, timezone


# pobieranie lokalizacji i danych mqtt ze zmiennych środowiskowych
lokalizacja = os.getenv("LOCATIONS")
STUDENT_ID = os.getenv("STUDENT_ID", "259910")
TOPIC = f"{STUDENT_ID}/{lokalizacja}"
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

#klasa WeatherRequester, w której są pobierane dane, które potem idą do mqtt w mqtt_module
class WeatherRequester:
    def __init__(self, location): #inicjalizacja klasy 
        self.location = location
        self.api_url = f"{API_URL}/{self.location}"
        self.headers = {"X-API-Key": API_KEY}
   
        
    def fetch_data(self): #pobieranie danych pogodowych
        while True:
            try:
                # wysyłanie żądania GET do api z nagłówkami
                response = requests.get(self.api_url, headers=self.headers)

                # Sprawdzanie kodu odpowiedzi
                if response.status_code == 200:
                    data = response.json()

                    # pobranie danych na podstawie ostatniej aktualizacji z api
                    results = data.get("results", []) #nazwa klucza w odpowiedzi api, który zawiera listę wyników, "results"- tablica obiektów json, z których każdy zawiera szczegóły dotyczące lokalizacji
                    
                    if results:
                        last_updated = results[0].get("lastUpdated", "") #przypisane do last_updated pierwszej pozycji z tablicy results i get na lastupdated, domyslnie nic 
                        system_timestamp = datetime.now(timezone.utc).isoformat()
                        location_name = results[0].get("city", str(self.location)) #przypisane do location name tekstu z nazwa lokalizacji pobrana z api

                        return {

                            # formatka wiadomosci
                            "location": self.location,
                            "location_name": location_name,  
                            "timestamp": system_timestamp, 
                            "lastUpdated_from_api": last_updated, 
                            "values": [
                            #parametry
                                {
                                    param["parameter"]: param["lastValue"]
                                }
                                for param in data["results"][0]["parameters"]
                            ]
                        }

                    else:
                        print("Brak wyników w odpowiedzi API.")

                else:
                     print(f"Błąd API: {response.status_code}")

            
            except Exception as e:
                print(f"Nie pobrano danych {e}")

            return None #nic nie zwraca


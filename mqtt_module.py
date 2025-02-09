import paho.mqtt.client as mqtt  # moduł do obsługi komunikacji mqtt
import json  # moduł do przetwarzania danych w formacie json
import os  # moduł do pracy z systemem plików i zmiennymi środowiskowymi
import time  # moduł do operacji związanych z czasem
from datetime import datetime, timezone  # klasy do pracy z czasem i strefami czasowymi
from w_requester import WeatherRequester  # import klasy WeatherRequester


# pobieranie konfiguracji ze zmiennych środowiskowych
BROKER_ADDRESS = os.getenv("BROKER_ADDRESS", "localhost")  # adres brokera MQTT 
BROKER_PORT = int(os.getenv("BROKER_PORT", 1883))  # port brokera MQTT 
MQTT_USER = os.getenv("MQTT_USER", "user")  # nazwa użytkownika do logowania na brokerze mqtt
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "password")  # hasło do brokera 
DATA_FOLDER = os.getenv("DATA_FOLDER", "./data")  # ścieżka do folderu, w którym zapisywane są dane json
STUDENT_ID = os.getenv("STUDENT_ID", "259910")  # indeks
LOCATIONS = os.getenv("LOCATIONS", "10890")  # ID lokalizacji do pobierania danych pogodowych
TOPIC_PATTERN = "#"  # subskrypcja na wszystkie wiadomości


# inicjalizacja mqtt
class MQTTModule:
    def __init__(self, broker_address, broker_port, username, password, student_id, location):
        self.client = mqtt.Client()  # tworzenie klienta MQTT
        self.client.username_pw_set(username, password)  # ustawienie danych logowania (użytkownik i hasło)
        self.client.connect(broker_address, broker_port)  # połączenie z brokerem mqtt
        self.client.on_message = self.on_message  # ustawienie funkcji obsługującej odebrane wiadomości

        self.student_id = student_id  # przechowywanie indeksu
        self.location = location  # przechowywanie lokalizacji
        self.topic = f"{student_id}/{location}"  # konstrukcja topica 
       
        os.makedirs(DATA_FOLDER, exist_ok=True)  # stworzenie folderu na dane, jeśli nie istnieje
        self.weather_requester = WeatherRequester(location) #inicjalizacja klasy WeatherRequester

# publikowanie wiadomości
    def publish_message(self, topic, message):
        result = self.client.publish(topic, message, qos=1)  # publikowanie wiadomości na wskazanym topicu
        if result.rc != mqtt.MQTT_ERR_SUCCESS:  # jeśli publikacja się nie powiodła to błąd
            print(f"Nieopublikowano: {mqtt.error_string(result.rc)}")
        else:
            print(f"Wiadomość opublikowana jako {topic}")


# zapis danych do json
    def save_data_to_file(self, student_id, location, location_name, data):
        file_name = f"{student_id}-{location_name}.json"  # nazwa pliku
        file_path = os.path.join(DATA_FOLDER, file_name)  # ścieżka pliku

        with open(file_path, "w") as f:  # otwieranie pliku w trybie zapisu
            json.dump(data, f, indent=4)  # zapisanie danych w formacie json

        print(f"Data saved to {file_path}")  # print info o zapisaniu danych


#obsługa wiadomości
    def on_message(self, client, userdata, message):
        try:
            topic = message.topic  # pobieraniu topicu
            payload = message.payload.decode("utf-8")  # dekodowanie treści wiadomości 
            data = json.loads(payload)  # parsowanie danych json

            topic_parts = topic.split("/")  # rozdzielanie topicu na części przez /
            student_id = topic_parts[0]  # odwołanie do pierwszej pozycji jako indeks
            location = (topic_parts[1])  # odwołanie do drugiej pozycji jako lokalizacja

            location_name = data.get("location_name", str(location))  # pobieranie nazwy lokalizacji

            self.save_data_to_file(student_id, location, location_name, data)  # zapis danych do pliku

        except Exception as e:  # obsługa błędów w trakcie przetwarzania wiadomości
            print(f"Błąd podczas przetwarzania wiadomości: {e}")


#pobieranie danych pogodowych
    def fetch_weather_data(self):
        try:
           data = self.weather_requester.fetch_data() #pobieranie danych z klasy WeatherRequester z w_requester
           if data: #jeśli jakies sa
                self.publish_message(self.topic, json.dumps(data)) #to opublikuj

        except Exception as e:  # obsługa błędów 
            print(f"Błąd podczas pobierania danych pogodowych: {e}")


#pętla główna
    def run(self):
        self.client.subscribe(TOPIC_PATTERN)  # subskrybowanie na wskazany topic
        self.client.loop_start()  # pętla klienta mqtt

        try:
            while True:  # npętla
                self.fetch_weather_data()  # pobieranie danych z api z funkcji fetch weather data
                time.sleep(30)  # czekanie 30 sekund, zeby pobierac dane co 30 sekund
        except KeyboardInterrupt:  # obsługa przerwania programu (ctrl+c)
            print("Zatrzymano klienta MQTT.")
        finally:
            self.client.loop_stop()  # zatrzymanie pętli klienta mqtt
            self.client.disconnect()  # rozłączenie z brokerem mqtt

# uruchamianie aplikacji
if __name__ == "__main__":
    # tworzenie obiektu MQTTModule i uruchamianie
    mqtt_module = MQTTModule(
        BROKER_ADDRESS, BROKER_PORT, MQTT_USER, MQTT_PASSWORD, STUDENT_ID, LOCATIONS
    )
    mqtt_module.run()

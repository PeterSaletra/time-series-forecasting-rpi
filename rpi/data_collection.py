# data_collection.py
import Adafruit_DHT
import csv
import time
from datetime import datetime

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4
CSV_FILE = 'temperature_data.csv'

while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        with open(CSV_FILE, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now(), temperature])
    time.sleep(300)  # Odczyt co 5 minut
import Adafruit_DHT
import time

# Wybierz typ czujnika: DHT11 lub DHT22
sensor = Adafruit_DHT.DHT11  # lub Adafruit_DHT.DHT11

# Podaj numer pinu GPIO (nie numer pinu fizycznego)
gpio_pin = 4  # np. GPIO4 (pin fizyczny 7)

def read_dht():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio_pin)

    if humidity is not None and temperature is not None:
        print(f'Temperatura: {temperature:.1f}°C')
        print(f'Wilgotność: {humidity:.1f}%')
    else:
        print('Nie udało się odczytać danych z czujnika')

if __name__ == "__main__":
    try:
        while True:
            read_dht()
            time.sleep(2)  # odczyt co 2 sekundy
    except KeyboardInterrupt:
        print("Zatrzymano przez użytkownika.")


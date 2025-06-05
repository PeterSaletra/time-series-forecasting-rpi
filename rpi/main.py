import time
import torch
import numpy as np
import Adafruit_DHT
import RPi.GPIO as GPIO

# --- CONFIG ---
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4  # GPIO pin for DHT11
LED_PIN = 17  # GPIO pin for built-in LED
SEQUENCE_LENGTH = 24  # Must match your model
TARGET_INDEX = 0      # Only temperature
THRESHOLD = 1.0       # Degrees Celsius for "correct" prediction

# Use your scaler values from training (replace with your actual values)
SCALER_MEAN = 9.45    # Example: replace with scaler.mean_[0]
SCALER_STD = 8.42      # Example: replace with scaler.scale_[0]

# --- SETUP GPIO ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# --- LOAD MODEL ---
model = torch.jit.load("weather_lstm_model.pt")
model.eval()

# --- COLLECT INITIAL SEQUENCE ---
sequence = []

print("Collecting initial temperature readings...")
while len(sequence) < SEQUENCE_LENGTH:
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if temperature is not None:
        sequence.append([temperature])
        print(f"Reading {len(sequence)}/{SEQUENCE_LENGTH}: {temperature}°C")
    else:
        print("Sensor failure. Retrying...")
    time.sleep(2)

# --- MAIN LOOP ---
try:
    while True:
        # Scale input
        seq_np = np.array(sequence)
        seq_scaled = (seq_np - SCALER_MEAN) / SCALER_STD
        x_input = torch.tensor(seq_scaled, dtype=torch.float32).unsqueeze(0)  # (1, seq_len, 1)

        # Predict next temperature(s)
        with torch.no_grad():
            pred_scaled = model(x_input).squeeze(0)
        pred_temp = pred_scaled.numpy() * SCALER_STD + SCALER_MEAN
        predicted = float(pred_temp[0])  # Only first step

        # Read actual temperature
        humidity, actual_temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        print(f"Predicted: {predicted:.2f}°C, Actual: {actual_temp:.2f}°C")

        # Light LED if prediction is close
        if abs(predicted - actual_temp) <= THRESHOLD:
            GPIO.output(LED_PIN, GPIO.HIGH)
            print("LED ON: Prediction correct!")
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
            print("LED OFF: Prediction not correct.")

        # Update sequence
        sequence.append([actual_temp])
        sequence = sequence[-SEQUENCE_LENGTH:]

        time.sleep(10)  # Wait before next prediction

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Exiting...")

# ...end of file...
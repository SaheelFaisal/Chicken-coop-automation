import RPi.GPIO as GPIO
import data_logger
import time
import os

# GPIO Pin for PIR sensor
PIR_PIN = 17

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

data_logger.init_db()

def play_sound():
    os.system("paplay /usr/share/sounds/alsa/Noise.wav")

try:
    print("PIR Sensor Active. Waiting for motion...")

    while True:
        if GPIO.input(PIR_PIN):  # Motion detected
            print("Motion detected! Playing sound...")
            play_sound()
            data_logger.log_event()
            time.sleep(2)
        time.sleep(0.1) 

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()

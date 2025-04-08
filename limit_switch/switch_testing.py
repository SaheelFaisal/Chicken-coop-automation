import RPi.GPIO as GPIO
import time
import sqlite3
from datetime import datetime

LIMIT_SWITCH_PIN = 17  # GPIO Pin (e.g., GPIO17)

# Setup for GPIO and internal pull-up resistor
GPIO.setmode(GPIO.BCM)
GPIO.setup(LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize chicken count
chicken_count = 0

# Function to log the event time and the updated chicken count to the SQLite database
def log_event(count):
    conn = sqlite3.connect('chicken_events.db')
    c = conn.cursor()
    
    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS events (timestamp TEXT, chicken_count INTEGER)''')
    
    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Insert the timestamp and the updated chicken count into the database
    c.execute("INSERT INTO events (timestamp, chicken_count) VALUES (?, ?)", (timestamp, count))
    conn.commit()
    conn.close()

print("Monitoring limit switch...")

try:
    prev_state = GPIO.input(LIMIT_SWITCH_PIN)
    while True:
        current_state = GPIO.input(LIMIT_SWITCH_PIN)
        
        # Check for switch press (when previous state is HIGH and current state is LOW)
        if prev_state == GPIO.HIGH and current_state == GPIO.LOW:
            print("Switch PRESSED")
            
            # Increase the chicken count by 1
            chicken_count += 1
            print(f"Chicken Count: {chicken_count}")
            
            # Log the event timestamp and updated chicken count
            log_event(chicken_count)
        
        prev_state = current_state
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    GPIO.cleanup()


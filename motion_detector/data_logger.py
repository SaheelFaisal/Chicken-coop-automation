import sqlite3
import time

conn = sqlite3.connect("predator_data.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS detections (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  event TEXT)''')

def log_event():
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO detections (timestamp, event) VALUES (?, ?)", (timestamp, "Motion Detected"))
    conn.commit()

conn.close()


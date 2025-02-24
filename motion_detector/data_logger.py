import sqlite3
import time

# Function to initialize the database and create table if it doesn't exist
def init_db():
    conn = sqlite3.connect("../predator_data.db")
    cursor = conn.cursor()
    
    # Create the table if it does not exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS detections (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      timestamp TEXT,
                      event TEXT)''')
    
    conn.commit()
    conn.close()

# Function to log an event
def log_event():
    conn = sqlite3.connect("../predator_data.db")
    cursor = conn.cursor()
    
    # Insert event
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO detections (timestamp, event) VALUES (?, ?)", (timestamp, "Motion Detected"))
    
    conn.commit()
    conn.close()
    print("Event logged successfully!")

# Ensure the database is initialized when the script runs
if __name__ == "__main__":
    init_db()  # Create the table if it doesn’t exist
    log_event()  # Log an event


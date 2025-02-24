import data_logger
import time

data_logger.init_db()

for i in range(2):
    data_logger.log_event();
    print(f"Logged event {i + 1}/2")
    time.sleep(1)

print("Finished logging events")

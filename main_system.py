import threading
import time
from relay_polarity_control import PolarityRelayController
from relay_stepper_control import RelayStepperController
from sunset_sunrise_control import SunriseSunsetController
from motion_sound_system import motion_handler
from event_logger import log_event
import RPi.GPIO as GPIO

# Initialize components
actuator = PolarityRelayController()
stepper = RelayStepperController()
sun = SunriseSunsetController()

# GPIO setup for counters
LIMIT_SWITCH_PIN = 23
IR_SENSOR_PIN = 22
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(IR_SENSOR_PIN, GPIO.IN)

# Coop state
coop_closed = True
combo_count = 0

def open_coop():
    global coop_closed
    if not coop_closed:
        print("[COOP] Already open.")
        return
    print("[COOP] Opening...")
    actuator.retract()
    stepper.power_on()
    time.sleep(0.5)
    stepper.rotate("cw", 5)
    stepper.power_off()
    actuator.stop()
    coop_closed = False
    log_event("Coop Opened", "Daytime")

def close_coop():
    global coop_closed
    if coop_closed:
        print("[COOP] Already closed.")
        return
    print("[COOP] Closing...")
    actuator.extend()
    stepper.power_on()
    time.sleep(0.5)
    stepper.rotate("ccw", 5)
    stepper.power_off()
    actuator.stop()
    coop_closed = True
    log_event("Coop Closed", "Nighttime")

def auto_day_night_monitor():
    print("[AUTO] Starting day/night cycle monitoring...")
    while True:
        if sun.needs_update():
            sun.fetch_sun_times()

        state = sun.check_sun_times()
        if state == "open":
            open_coop()
        elif state == "close":
            close_coop()
        time.sleep(30)

def combo_counter_monitor(timeout=2):
    global combo_count
    print("[COMBO] Combo counter active (IR + Limit Switch)...")
    while True:
        if sun.check_sun_times() == "open":  # Daytime only
            ir_triggered = False
            limit_triggered = False
            start_time = None

            # Wait for either IR or Limit to trigger
            if GPIO.input(IR_SENSOR_PIN) == GPIO.LOW:
                ir_triggered = True
                start_time = time.time()
                print("[COMBO] IR triggered, waiting for Limit Switch...")
            elif GPIO.input(LIMIT_SWITCH_PIN) == GPIO.LOW:
                limit_triggered = True
                start_time = time.time()
                print("[COMBO] Limit Switch triggered, waiting for IR...")

            # Once one is triggered, wait up to 'timeout' seconds for the other
            if start_time:
                while time.time() - start_time < timeout:
                    if not limit_triggered and GPIO.input(LIMIT_SWITCH_PIN) == GPIO.LOW:
                        limit_triggered = True
                        print("[COMBO] Limit Switch triggered!")

                    if not ir_triggered and GPIO.input(IR_SENSOR_PIN) == GPIO.LOW:
                        ir_triggered = True
                        print("[COMBO] IR triggered!")

                    if ir_triggered and limit_triggered:
                        combo_count += 1
                        print(f"[COMBO] Valid chicken detected! Total: {combo_count}")
                        log_event("Combo Chicken Count", f"Combo Count: {combo_count}")
                        time.sleep(5)
                        break  # Successful combo!

                if not (ir_triggered and limit_triggered):
                    print("[COMBO] False count detected (only one sensor triggered or timeout).")
                    log_event("Combo Count Failed", "False trigger or timeout")
            time.sleep(0.1)
        else:
            time.sleep(5)  # Sleep longer at night since counting is inactive

def run_all_modules():
    threads = [
        threading.Thread(target=auto_day_night_monitor),
        threading.Thread(target=motion_handler),
        threading.Thread(target=combo_counter_monitor)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == "__main__":
    try:
        run_all_modules()
    except KeyboardInterrupt:
        print("[SYSTEM] Shutting down.")
        GPIO.cleanup()

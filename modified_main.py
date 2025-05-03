import threading
import time
import RPi.GPIO as GPIO
from relay_polarity_control import PolarityRelayController
from relay_stepper_control import RelayStepperController
from sunset_sunrise_control import SunriseSunsetController
from motion_sound_system import motion_handler
from event_logger import log_event

# --- GPIO Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Pins
LIMIT_SWITCH_PIN   = 23
IR_SENSOR_PIN      = 22
MODE_SWITCH_PIN    = 13  # AUTO <-> MANUAL
DAY_NIGHT_SWITCH_PIN = 4  # DAY <-> NIGHT in manual

GPIO.setup(LIMIT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(IR_SENSOR_PIN, GPIO.IN)
GPIO.setup(MODE_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DAY_NIGHT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- Controllers & State ---
actuator   = PolarityRelayController()
stepper    = RelayStepperController()
sun        = SunriseSunsetController()

motion_stop   = threading.Event()
motion_thread = None

coop_closed    = True
manual_mode    = False
manual_daytime = True
combo_count    = 0

# --- Coop Control ---
def extend_coop():
    global coop_closed
    actuator.extend()
    time.sleep(15)
    actuator.stop()
    stepper.power_on()
    stepper.rotate("ccw", 5)
    stepper.power_off()
    coop_closed = True
    log_event("Coop Closed", "Nighttime")
    print("[COOP] Coop closed.")

def retract_coop():
    global coop_closed
    actuator.retract()
    time.sleep(15)
    actuator.stop()
    stepper.power_on()
    stepper.rotate("cw", 5)
    stepper.power_off()
    coop_closed = False
    log_event("Coop Opened", "Daytime")
    print("[COOP] Coop opened.")

# --- Counting Logic ---
def combo_counter_loop():
    global combo_count
    print("[COMBO] Counter active (DAY).")
    while is_daytime():
        ir = GPIO.input(IR_SENSOR_PIN) == GPIO.LOW
        ls = GPIO.input(LIMIT_SWITCH_PIN) == GPIO.LOW
        if ir or ls:
            start = time.time()
            # 2-second window to catch both triggers
            while time.time() - start < 2:
                if not ir and GPIO.input(IR_SENSOR_PIN) == GPIO.LOW:
                    ir = True
                if not ls and GPIO.input(LIMIT_SWITCH_PIN) == GPIO.LOW:
                    ls = True
                if ir and ls:
                    combo_count += 1
                    print(f"[COMBO] Chicken counted! Total: {combo_count}")
                    log_event("Chicken Count", f"Total: {combo_count}")
                    time.sleep(2)
                    break
                time.sleep(0.05)
        time.sleep(0.1)

# --- Day/Night Determination ---
def is_daytime():
    return manual_daytime if manual_mode else sun.check_sun_times() == "open"

def switch_to_manual():
    global manual_mode
    manual_mode = True
    print("[MODE] Switched to MANUAL MODE.")

def switch_to_auto():
    global manual_mode
    manual_mode = False
    print("[MODE] Switched to AUTO MODE.")

def switch_day_night_manual():
    global manual_daytime
    manual_daytime = not manual_daytime
    print(f"[TIME] Switched to {'DAYTIME' if manual_daytime else 'NIGHTTIME'}." )

# --- Monitor Physical Switches ---
def monitor_mode_switch():
    prev_mode = GPIO.input(MODE_SWITCH_PIN)
    prev_dn   = GPIO.input(DAY_NIGHT_SWITCH_PIN)
    while True:
        time.sleep(0.1)
        curr_mode = GPIO.input(MODE_SWITCH_PIN)
        if curr_mode != prev_mode and curr_mode == GPIO.LOW:
            switch_to_manual() if not manual_mode else switch_to_auto()
        prev_mode = curr_mode
        if manual_mode:
            curr_dn = GPIO.input(DAY_NIGHT_SWITCH_PIN)
            if curr_dn != prev_dn and curr_dn == GPIO.LOW:
                switch_day_night_manual()
            prev_dn = curr_dn

# --- Nighttime Logic ---
def run_nighttime():
    global motion_thread
    if coop_closed:
        retract_coop()

    # Start or restart motion thread
    if motion_thread is None or not motion_thread.is_alive():
        motion_stop.clear()
        motion_thread = threading.Thread(
            target=motion_handler,
            args=(motion_stop,),
            daemon=True
        )
        motion_thread.start()

    # Stay in night mode until day arrives
    while not is_daytime():
        time.sleep(1)

    # Tear down motion thread
    motion_stop.set()
    motion_thread.join()
    motion_thread = None
    print("[SYSTEM] Exited NIGHT mode.")

# --- Daytime Logic ---
def run_daytime():
    if not coop_closed:
        extend_coop()

    # Ensure motion thread is stopped
    if motion_thread and motion_thread.is_alive():
        motion_stop.set()
        motion_thread.join()

    combo_counter_loop()

# --- Main Loop ---
def main_loop():
    threading.Thread(target=monitor_mode_switch, daemon=True).start()
    while True:
        if is_daytime():
            print("[SYSTEM] DAYTIME")
            run_daytime()
        else:
            print("[SYSTEM] NIGHTTIME")
            run_nighttime()

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("[SYSTEM] Shutting down…")
    finally:
        GPIO.cleanup()  

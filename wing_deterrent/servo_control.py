import pigpio
import time

SERVO_PIN = 18  # GPIO18 (physical pin 12)

# Initialize pigpio and set mode
pi = pigpio.pi()
pi.set_mode(SERVO_PIN, pigpio.OUTPUT)

# Function to set servo angle
def set_angle(angle):
    pulse_width = 500 + int((angle / 180.0) * 2000)
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)

try:
    print("Moving servo to 0°")
    set_angle(0)
    time.sleep(1)

    print("Moving to 90°")
    set_angle(90)
    time.sleep(1)

    print("Moving to 180°")
    set_angle(180)
    time.sleep(1)

    print("Back to 90°")
    set_angle(90)
    time.sleep(1)

finally:
    print("Releasing servo")
    pi.set_servo_pulsewidth(SERVO_PIN, 0)
    pi.stop()

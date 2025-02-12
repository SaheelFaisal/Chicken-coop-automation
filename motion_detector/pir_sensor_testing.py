
from gpiozero import MotionSensor, LED
import time

pir = MotionSensor(17)
led = LED(22)

while True:
    pir.wait_for_motion()
    led.on()
    pir.wait_for_no_motion()
    led.off()

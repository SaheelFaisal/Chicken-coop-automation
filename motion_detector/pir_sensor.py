from gpiozero import MotionSensor

def pir_sensor():
    pir = MotionSensor(17)

    while True:
        pir.wait_for_motion()
        print("Motion Detected")

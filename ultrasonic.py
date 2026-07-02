from machine import Pin,time_pulse_us
from time import sleep_us

class UltrasonicSensor:
    def __init__(self,trig,echo):
        self.trig=Pin(trig,Pin.OUT,value=0)
        self.echo=Pin(echo,Pin.IN)

    def read_cm(self):
        self.trig.value(0); sleep_us(2)
        self.trig.value(1); sleep_us(10)
        self.trig.value(0)
        duration=time_pulse_us(self.echo,1,30000)
        return None if duration<0 else duration/58


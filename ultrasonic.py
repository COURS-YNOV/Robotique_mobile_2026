from machine import Pin,time_pulse_us
from time import sleep_us
class UltrasonicSensor:
 def __init__(self,trig,echo):
  self.trig=Pin(trig,Pin.OUT); self.echo=Pin(echo,Pin.IN); self.trig.value(0)
 def read_cm(self):
  self.trig.value(0); sleep_us(2); self.trig.value(1); sleep_us(10); self.trig.value(0)
  d=time_pulse_us(self.echo,1,30000)
  return None if d<0 else d/58

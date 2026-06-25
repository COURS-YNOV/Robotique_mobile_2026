import machine, time
from machine import Pin

class Sensor_Captor:
    def __init__(self, trigger_pin, echo_pin, distance_max = 400):
        self.trigger = Pin(trigger_pin, mode=Pin.OUT)
        self.echo = Pin(echo_pin, mode=Pin.IN)
        self.distance_max = distance_max*2
        
    def _send_pulse_and_wait(self):
        self.trigger.value(0)
        time.sleep_us(2)
        self.trigger.value(1)
        time.sleep_us(10)
        self.trigger.value(0)
        pulse_time = machine.time_pulse_us(self.echo, 1, distance_max*30)
        return pulse_time
    
    def distance(self):
        pulse_time = self._send_pulse_and_wait()
        cms = (pulse_time / 2) /29.1 #C'est la formule qui permet de convertir les données microsecondes en cm.
        return cms
    
    def request_ultrasonic(self):
        distance = self.distance()
        return distance

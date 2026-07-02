from machine import Pin
class StatusLeds:
 def __init__(self,p1,p2): self.a=Pin(p1,Pin.OUT); self.b=Pin(p2,Pin.OUT)
 def set(self,a=False,b=False): self.a.value(a); self.b.value(b)

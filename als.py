from machine import Pin,SPI
class PmodALS:
 def __init__(self,cs,sdo,sck):
  self.cs=Pin(cs,Pin.OUT,value=1)
  self.spi=SPI(1,baudrate=1000000,polarity=0,phase=0,sck=Pin(sck),miso=Pin(sdo),mosi=None)
 def read_raw(self):
  b=bytearray(2); self.cs.value(0); self.spi.readinto(b); self.cs.value(1)
  return (((b[0]<<8)|b[1])>>4)&255
 def read_percent(self): return self.read_raw()*100/255

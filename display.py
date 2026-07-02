from machine import Pin,I2C
import ssd1306
class Display:
 def __init__(self,sda,scl):
  try:
   self.i2c=I2C(0,sda=Pin(sda),scl=Pin(scl),freq=400000)
   print("I2C:",self.i2c.scan()); self.oled=ssd1306.SSD1306_I2C(128,64,self.i2c); self.ok=True
  except Exception as e: print("OLED:",e); self.ok=False
 def show(self,d,l,s):
  if not self.ok:return
  self.oled.fill(0); self.oled.text("ESP32-C6",0,0); self.oled.text("Etat:"+s,0,16)
  self.oled.text("Dist:N/A" if d is None else "Dist:{:.1f}cm".format(d),0,32)
  self.oled.text("Lum:{:.0f}%".format(l),0,48); self.oled.show()

from machine import Pin,PWM
class MotorDriver:
 def __init__(self,in1,in2,ena,in3,in4,enb,enabled=False):
  self.enabled=enabled
  if enabled:
   self.in1=Pin(in1,Pin.OUT); self.in2=Pin(in2,Pin.OUT)
   self.in3=Pin(in3,Pin.OUT); self.in4=Pin(in4,Pin.OUT)
   self.ena=PWM(Pin(ena),freq=1000); self.enb=PWM(Pin(enb),freq=1000)
 def _duty(self,s): return int(max(0,min(100,abs(s)))*65535/100)
 def _one(self,a,b,pwm,s):
  a.value(1 if s>0 else 0); b.value(1 if s<0 else 0); pwm.duty_u16(self._duty(s))
 def set_speeds(self,l,r):
  if not self.enabled:
   print("[MOTEURS OFF]",l,r); return
  self._one(self.in1,self.in2,self.ena,l); self._one(self.in3,self.in4,self.enb,r)
 def forward(self,s): self.set_speeds(s,s)
 def turn_right(self,s): self.set_speeds(s,-s)
 def stop(self): self.set_speeds(0,0)

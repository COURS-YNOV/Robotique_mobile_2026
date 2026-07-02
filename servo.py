from machine import Pin,PWM
class Servo:
 def __init__(self,pin): self.pwm=PWM(Pin(pin),freq=50)
 def set_angle(self,a):
  a=max(0,min(180,a)); self.pwm.duty_u16(int(1638+(a/180)*(8192-1638)))

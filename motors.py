from machine import Pin,PWM

class MotorDriver:
    def __init__(self,in1,in2,ena,in3,in4,enb,enabled=True):
        self.enabled=enabled
        self.in1=Pin(in1,Pin.OUT); self.in2=Pin(in2,Pin.OUT)
        self.in3=Pin(in3,Pin.OUT); self.in4=Pin(in4,Pin.OUT)
        self.ena=PWM(Pin(ena),freq=1000,duty_u16=0)
        self.enb=PWM(Pin(enb),freq=1000,duty_u16=0)
        self.stop()

    def _drive(self,a,b,pwm,speed):
        if speed>0: a.value(1); b.value(0)
        elif speed<0: a.value(0); b.value(1)
        else: a.value(0); b.value(0)
        duty=int(min(100,abs(speed))*65535/100) if self.enabled else 0
        pwm.duty_u16(duty)

    def set(self,left,right):
        self._drive(self.in1,self.in2,self.ena,left)
        self._drive(self.in3,self.in4,self.enb,right)

    def forward(self,s): self.set(s,s)
    def backward(self,s): self.set(-s,-s)
    def left(self, s):self.set(s, -s)
    def right(self, s):self.set(-s, s)
    def stop(self): self.set(0,0)


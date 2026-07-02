from machine import Pin,PWM

class Servo:
    def __init__(self,pin):
        self.pwm=PWM(Pin(pin),freq=50)

    def set_angle(self,angle):
        angle=max(0,min(180,int(angle)))
        pulse_us=500+int(angle*2000/180)
        self.pwm.duty_ns(pulse_us*1000)


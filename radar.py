from time import ticks_ms,ticks_diff

class Radar:
    def __init__(self,servo,sensor,min_angle,max_angle,step,delay_ms):
        self.servo=servo
        self.sensor=sensor
        self.min=min_angle
        self.max=max_angle
        self.step=abs(step)
        self.delay=delay_ms
        self.angle=min_angle
        self.direction=1
        self.distance=None
        self.last=ticks_ms()
        self.servo.set_angle(self.angle)

    def update(self):
        if ticks_diff(ticks_ms(),self.last)<self.delay:
            return False

        self.last=ticks_ms()
        self.angle+=self.step*self.direction

        if self.angle>=self.max:
            self.angle=self.max
            self.direction=-1
        elif self.angle<=self.min:
            self.angle=self.min
            self.direction=1

        self.servo.set_angle(self.angle)
        self.distance=self.sensor.read_cm()
        return True


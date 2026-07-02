from time import sleep_ms
import config
from ultrasonic import UltrasonicSensor
from motors import MotorDriver
from servo import Servo
from leds import StatusLeds
from als import PmodALS
from display import Display

sensor=UltrasonicSensor(config.ULTRASON_TRIG,config.ULTRASON_ECHO)
motors=MotorDriver(config.MOTOR_IN1,config.MOTOR_IN2,config.MOTOR_ENA,config.MOTOR_IN3,config.MOTOR_IN4,config.MOTOR_ENB,config.MOTORS_ENABLED)
servo=Servo(config.SERVO_PIN)
leds=StatusLeds(config.LED_1_PIN,config.LED_2_PIN)
als=PmodALS(config.ALS_CS,config.ALS_SDO,config.ALS_SCK)
display=Display(config.OLED_SDA,config.OLED_SCL)
servo.set_angle(config.SERVO_CENTER_ANGLE)

def state(d):
 if d is None:return "ERREUR"
 if d<20:return "DANGER"
 if d<50:return "ALERTE"
 if d<100:return "ATTENTION"
 return "LIBRE"

while True:
 try:
  d=sensor.read_cm(); l=als.read_percent(); s=state(d)
  print("Distance:",d,"cm | Lumiere:{:.1f}% |".format(l),s)
  if s in ("ERREUR","DANGER"): motors.stop(); leds.set(1,1)
  elif s=="ALERTE": motors.turn_right(config.MOTOR_TURN_SPEED); leds.set(1,0)
  elif s=="ATTENTION": motors.forward(25); leds.set(0,1)
  else: motors.forward(config.MOTOR_BASE_SPEED); leds.set(0,0)
  display.show(d,l,s)
 except Exception as e: print("Erreur:",e)
 sleep_ms(config.LOOP_DELAY_MS)

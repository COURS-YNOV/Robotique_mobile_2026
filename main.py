from time import sleep_ms,ticks_ms,ticks_diff
import config
from motors import MotorDriver
from servo import Servo
from ultrasonic import UltrasonicSensor
from radar import Radar
from display import Display
from wifi_control import connect_wifi,WebController

motors=MotorDriver(config.MOTOR_IN1,config.MOTOR_IN2,config.MOTOR_ENA,
                   config.MOTOR_IN3,config.MOTOR_IN4,config.MOTOR_ENB,
                   config.MOTORS_ENABLED)

servo=Servo(config.SERVO_PIN)
sensor=UltrasonicSensor(config.ULTRASON_TRIG,config.ULTRASON_ECHO)
radar=Radar(servo,sensor,config.RADAR_MIN_ANGLE,config.RADAR_MAX_ANGLE,
            config.RADAR_STEP_DEG,config.RADAR_STEP_DELAY_MS)
display=Display(config.OLED_SDA,config.OLED_SCL)

ip=connect_wifi(config.WIFI_SSID,config.WIFI_PASSWORD)
web=WebController()
last_display=0

while True:
    try:
        web.poll()
        radar.update()
        web.distance=radar.distance
        web.angle=radar.angle

        if ticks_diff(ticks_ms(),web.last)>config.COMMAND_TIMEOUT_MS:
            web.command="stop"

        cmd=web.command
        speed=web.speed

        if cmd=="forward" and radar.distance is not None and radar.distance<=config.STOP_DISTANCE_CM:
            motors.stop()
        elif cmd=="forward": motors.forward(speed)
        elif cmd=="backward": motors.backward(speed)
        elif cmd=="left": motors.left(speed)
        elif cmd=="right": motors.right(speed)
        else: motors.stop()

        if ticks_diff(ticks_ms(),last_display)>120:
            last_display=ticks_ms()
            display.show(ip,cmd,speed,radar.angle,radar.distance)

    except Exception as e:
        motors.stop()
        print("Erreur:",e)

    sleep_ms(10)


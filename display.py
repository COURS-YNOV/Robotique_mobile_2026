from machine import Pin, I2C
import ssd1306


class Display:
    def __init__(self, sda, scl):
        self.ok = False

        try:
            i2c = I2C(
                0,
                sda=Pin(sda),
                scl=Pin(scl),
                freq=100000
            )

            devices = i2c.scan()
            print("I2C :", devices)

            self.oled = ssd1306.SSD1306_I2C(
                128,
                64,
                i2c,
                addr=0x3C
            )

            self.ok = True

        except Exception as exc:
            print("Erreur OLED :", exc)

    @staticmethod
    def _limit(value, minimum, maximum):
        return max(minimum, min(maximum, value))

    def _draw_normal_eye(self, center_x, center_y, pupil_offset):
        eye_width = 42
        eye_height = 28

        eye_x = center_x - eye_width // 2
        eye_y = center_y - eye_height // 2

        # Contour rectangulaire arrondi visuellement
        self.oled.rect(
            eye_x,
            eye_y,
            eye_width,
            eye_height,
            1
        )

        # Coins légèrement effacés pour arrondir la forme
        self.oled.pixel(eye_x, eye_y, 0)
        self.oled.pixel(eye_x + eye_width - 1, eye_y, 0)
        self.oled.pixel(eye_x, eye_y + eye_height - 1, 0)
        self.oled.pixel(
            eye_x + eye_width - 1,
            eye_y + eye_height - 1,
            0
        )

        pupil_width = 10
        pupil_height = 16

        pupil_x = (
            center_x
            + pupil_offset
            - pupil_width // 2
        )

        pupil_y = center_y - pupil_height // 2

        self.oled.fill_rect(
            pupil_x,
            pupil_y,
            pupil_width,
            pupil_height,
            1
        )

        # Petit reflet dans la pupille
        self.oled.fill_rect(
            pupil_x + 2,
            pupil_y + 2,
            3,
            3,
            0
        )

    def _draw_alert_eye(self, center_x, center_y, left_eye):
        eye_width = 42
        eye_height = 24

        x = center_x - eye_width // 2
        y = center_y - eye_height // 2

        # Forme agressive lorsque l'obstacle est proche
        if left_eye:
            self.oled.line(x, y, x + eye_width, y + 7, 1)
        else:
            self.oled.line(x, y + 7, x + eye_width, y, 1)

        self.oled.line(
            x,
            y + eye_height,
            x + eye_width,
            y + eye_height,
            1
        )

        self.oled.line(
            x,
            y,
            x,
            y + eye_height,
            1
        )

        self.oled.line(
            x + eye_width,
            y + 7,
            x + eye_width,
            y + eye_height,
            1
        )

        self.oled.fill_rect(
            center_x - 5,
            center_y - 4,
            10,
            13,
            1
        )

    def _draw_closed_eye(self, center_x, center_y):
        # Œil fermé pour l'état STOP
        self.oled.line(
            center_x - 20,
            center_y,
            center_x + 20,
            center_y,
            1
        )

        self.oled.line(
            center_x - 15,
            center_y,
            center_x - 10,
            center_y + 4,
            1
        )

        self.oled.line(
            center_x + 10,
            center_y + 4,
            center_x + 15,
            center_y,
            1
        )

    def _draw_eyes(self, command, angle, distance):
        left_x = 34
        right_x = 94
        center_y = 27

        command = command.lower()

        # Déplacement des pupilles selon le radar
        pupil_offset = int((angle - 90) / 2)
        pupil_offset = self._limit(pupil_offset, -10, 10)

        danger = (
            distance is not None
            and distance <= 20
        )

        if danger:
            self._draw_alert_eye(
                left_x,
                center_y,
                True
            )

            self._draw_alert_eye(
                right_x,
                center_y,
                False
            )

        elif command == "stop":
            self._draw_closed_eye(
                left_x,
                center_y
            )

            self._draw_closed_eye(
                right_x,
                center_y
            )

        else:
            self._draw_normal_eye(
                left_x,
                center_y,
                pupil_offset
            )

            self._draw_normal_eye(
                right_x,
                center_y,
                pupil_offset
            )

    def show(
        self,
        ip,
        command,
        speed,
        angle,
        distance
    ):
        if not self.ok:
            return

        self.oled.fill(0)

        self._draw_eyes(
            command,
            angle,
            distance
        )

        if distance is None:
            distance_text = "N/A"
        else:
            distance_text = "{:.0f}cm".format(distance)

        # Bande inférieure d'informations
        self.oled.text(
            distance_text,
            2,
            53
        )

        self.oled.text(
            "{}%".format(speed),
            50,
            53
        )

        self.oled.text(
            "{}d".format(angle),
            91,
            53
        )

        self.oled.show()

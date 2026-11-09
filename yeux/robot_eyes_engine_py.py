import time
import math
import numpy
import cv2
from PIL import Image, ImageDraw


class RobotEyes:

    def __init__(self, rotation=90):

        # ==================================================
        # ST7735 DISPLAY ÉCRAN À CONFIGURER
        # ==================================================

        # self.disp = st7735.ST7735(
        #     port=0,
        #     cs=st7735.BG_SPI_CS_BACK,
        #     dc="GPIO24",
        #     backlight="GPIO22",
        #     rst="GPIO25",
        #     rotation=rotation,
        #     invert=False,
        #     spi_speed_hz=4000000
        # )

        # self.disp.begin()

        # Display size after rotation=90
        self.WIDTH = 160
        self.HEIGHT = 124

        # ==================================================
        # EYE SETTINGS
        # ==================================================

        self.eye_width = 38
        self.eye_height = 52

        self.left_x = 25
        self.right_x = 97

        self.center_y = 36

        # Current eye movement
        self.offset_x = 0
        self.offset_y = 0

        # Current expression
        self.expression = "normal"

        # Colors
        self.background = (0, 0, 0)
        self.eye_color = (100, 200, 255)

        self.draw()


    # ======================================================
    # CREATE IMAGE
    # ======================================================

    def create_image(self):

        return Image.new(
            "RGB",
            (self.WIDTH, self.HEIGHT),
            self.background
        )


    # ======================================================
    # DRAW ONE EYE
    # ======================================================

    def draw_eye(self, draw, x, y):

        w = self.eye_width
        h = self.eye_height

        # Apply smooth eye movement
        x += self.offset_x
        y += self.offset_y


        # --------------------------------------------------
        # NORMAL
        # --------------------------------------------------

        if self.expression == "normal":

            draw.rounded_rectangle(
                (
                    x,
                    y,
                    x + w,
                    y + h
                ),
                radius=10,
                fill=self.eye_color
            )


        # --------------------------------------------------
        # HAPPY
        # --------------------------------------------------

        elif self.expression == "happy":

            draw.arc(
                (
                    x,
                    y + 5,
                    x + w,
                    y + h + 15
                ),
                200,
                340,
                fill=self.eye_color,
                width=6
            )


        # --------------------------------------------------
        # ANGRY
        # --------------------------------------------------

        elif self.expression == "angry":

            draw.polygon(
                [
                    (x, y + 12),
                    (x + w, y),
                    (x + w, y + h),
                    (x, y + h - 8)
                ],
                fill=self.eye_color
            )


        # --------------------------------------------------
        # SURPRISED
        # --------------------------------------------------

        elif self.expression == "surprised":

            draw.rounded_rectangle(
                (
                    x - 3,
                    y - 6,
                    x + w + 3,
                    y + h + 6
                ),
                radius=14,
                fill=self.eye_color
            )


        # --------------------------------------------------
        # SLEEP
        # --------------------------------------------------

        elif self.expression == "sleep":

            draw.rounded_rectangle(
                (
                    x + 5,
                    y + h // 2 - 3,
                    x + w - 5,
                    y + h // 2 + 3
                ),
                radius=3,
                fill=self.eye_color
            )


        # --------------------------------------------------
        # BLINK
        # --------------------------------------------------

        elif self.expression == "blink":

            draw.rounded_rectangle(
                (
                    x + 4,
                    y + h // 2 - 3,
                    x + w - 4,
                    y + h // 2 + 3
                ),
                radius=3,
                fill=self.eye_color
            )


        # --------------------------------------------------
        # WINK LEFT
        # --------------------------------------------------

        elif self.expression == "wink_left":

            if x < self.WIDTH // 2:

                draw.rounded_rectangle(
                    (
                        x + 4,
                        y + h // 2 - 3,
                        x + w - 4,
                        y + h // 2 + 3
                    ),
                    radius=3,
                    fill=self.eye_color
                )

            else:

                draw.rounded_rectangle(
                    (
                        x,
                        y,
                        x + w,
                        y + h
                    ),
                    radius=10,
                    fill=self.eye_color
                )


        # --------------------------------------------------
        # WINK RIGHT
        # --------------------------------------------------

        elif self.expression == "wink_right":

            if x >= self.WIDTH // 2:

                draw.rounded_rectangle(
                    (
                        x + 4,
                        y + h // 2 - 3,
                        x + w - 4,
                        y + h // 2 + 3
                    ),
                    radius=3,
                    fill=self.eye_color
                )

            else:

                draw.rounded_rectangle(
                    (
                        x,
                        y,
                        x + w,
                        y + h
                    ),
                    radius=10,
                    fill=self.eye_color
                )


        # --------------------------------------------------
        # LOOK UP
        # --------------------------------------------------

        elif self.expression == "look_up":

            draw.rounded_rectangle(
                (
                    x,
                    y - 8,
                    x + w,
                    y + h - 8
                ),
                radius=10,
                fill=self.eye_color
            )


        # --------------------------------------------------
        # LOOK DOWN
        # --------------------------------------------------

        elif self.expression == "look_down":

            draw.rounded_rectangle(
                (
                    x,
                    y + 8,
                    x + w,
                    y + h + 8
                ),
                radius=10,
                fill=self.eye_color
            )


        # --------------------------------------------------
        # DEFAULT
        # --------------------------------------------------

        else:

            draw.rounded_rectangle(
                (
                    x,
                    y,
                    x + w,
                    y + h
                ),
                radius=10,
                fill=self.eye_color
            )


    # ======================================================
    # DRAW BOTH EYES
    # ======================================================

    def draw(self):

        image = self.create_image()
        draw = ImageDraw.Draw(image)

        self.draw_eye(
            draw,
            self.left_x,
            self.center_y
        )

        self.draw_eye(
            draw,
            self.right_x,
            self.center_y
        )

        #self.disp.display(image) # À changer (à convertir plutôt) !
        imgtraduite = numpy.array(image)[:, :, ::-1].copy() # Slicing 
        cv2.imshow('Humeur du jour',imgtraduite)
        cv2.waitKey(1)

    # ======================================================
    # SMOOTH MOVEMENT
    # ======================================================

    def move(self, target_x, target_y, duration=0.5):

        start_x = self.offset_x
        start_y = self.offset_y

        fps = 30
        frames = max(1, int(duration * fps))

        for frame in range(frames + 1):

            progress = frame / frames

            # Smooth ease-in / ease-out
            smooth = (
                0.5
                - 0.5 * math.cos(progress * math.pi)
            )

            self.offset_x = int(
                start_x +
                (target_x - start_x) * smooth
            )

            self.offset_y = int(
                start_y +
                (target_y - start_y) * smooth
            )

            self.draw()

            time.sleep(1 / fps)


    # ======================================================
    # LOOK LEFT
    # ======================================================

    def look_left(self, duration=0.5):

        self.expression = "normal"

        self.move(
            -10,
            0,
            duration
        )


    # ======================================================
    # LOOK RIGHT
    # ======================================================

    def look_right(self, duration=0.5):

        self.expression = "normal"

        self.move(
            10,
            0,
            duration
        )


    # ======================================================
    # LOOK CENTER
    # ======================================================

    def look_center(self, duration=0.5):

        self.expression = "normal"

        self.move(
            0,
            0,
            duration
        )


    # ======================================================
    # LOOK UP
    # ======================================================

    def look_up(self, duration=0.5):

        self.expression = "normal"

        self.move(
            0,
            -8,
            duration
        )


    # ======================================================
    # LOOK DOWN
    # ======================================================

    def look_down(self, duration=0.5):

        self.expression = "normal"

        self.move(
            0,
            8,
            duration
        )


    # ======================================================
    # DIAGONAL LOOKING
    # ======================================================

    def look_up_left(self, duration=0.5):

        self.expression = "normal"

        self.move(
            -8,
            -7,
            duration
        )


    def look_up_right(self, duration=0.5):

        self.expression = "normal"

        self.move(
            8,
            -7,
            duration
        )


    def look_down_left(self, duration=0.5):

        self.expression = "normal"

        self.move(
            -8,
            7,
            duration
        )


    def look_down_right(self, duration=0.5):

        self.expression = "normal"

        self.move(
            8,
            7,
            duration
        )


    # ======================================================
    # EXPRESSIONS
    # ======================================================

    def normal(self):

        self.expression = "normal"
        self.draw()


    def happy(self):

        self.expression = "happy"
        self.draw()


    def angry(self):

        self.expression = "angry"
        self.draw()


    def surprised(self):

        self.expression = "surprised"
        self.draw()


    def sleep(self):

        self.expression = "sleep"
        self.draw()


    # ======================================================
    # BLINK
    # ======================================================

    def blink(self):

        previous = self.expression

        self.expression = "blink"
        self.draw()

        time.sleep(0.12)

        self.expression = previous
        self.draw()


    # ======================================================
    # DOUBLE BLINK
    # ======================================================

    def double_blink(self):

        self.blink()

        time.sleep(0.08)

        self.blink()


    # ======================================================
    # WINK
    # ======================================================

    def wink_left(self):

        self.expression = "wink_left"
        self.draw()

        time.sleep(0.3)

        self.normal()


    def wink_right(self):

        self.expression = "wink_right"
        self.draw()

        time.sleep(0.3)

        self.normal()


    # ======================================================
    # SET EXPRESSION
    # ======================================================

    def set_expression(self, expression):

        expression = expression.lower()

        valid = [
            "normal",
            "happy",
            "angry",
            "surprised",
            "sleep",
            "blink",
            "wink_left",
            "wink_right"
        ]

        if expression in valid:

            self.expression = expression
            self.draw()

        else:

            print("Unknown expression:", expression)


    # ======================================================
    # SCAN
    # ======================================================

    def scan(self):

        self.look_left(0.7)

        time.sleep(0.3)

        self.look_right(1.2)

        time.sleep(0.3)

        self.look_left(1.2)

        time.sleep(0.3)

        self.look_center(0.7)


    # ======================================================
    # ROBOT IDLE MOVEMENT
    # ======================================================

    def idle_animation(self):

        self.look_center(0.4)

        time.sleep(1.5)

        self.look_left(0.6)

        time.sleep(0.5)

        self.look_center(0.6)

        time.sleep(1)

        self.blink()

        time.sleep(1)

        self.look_right(0.6)

        time.sleep(0.5)

        self.look_center(0.6)


    # ======================================================
    # CLOSE
    # ======================================================

    def close(self):

        self.expression = "sleep"

        self.offset_x = 0
        self.offset_y = 0

        self.draw()

        time.sleep(0.2)

        try:
            cv2.destroyAllWindows()
        except:
            pass
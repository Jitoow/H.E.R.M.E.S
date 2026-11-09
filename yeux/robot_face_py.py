import time
import random
from robot_eyes_engine_py import RobotEyes


# ============================================================
# ROBOT FACE
# Fast + Smooth + Seamless Animation
# ============================================================

eyes = RobotEyes(rotation=90) # Objet crée dans le code importé au dessus que l'on va manipuler durant le reste du code


# ============================================================
# FAST LOOK
# ============================================================

def look_left():
    eyes.look_left(0.22)


def look_right():
    eyes.look_right(0.22)


def look_center():
    eyes.look_center(0.18)


def look_up():
    eyes.look_up(0.20)


def look_down():
    eyes.look_down(0.20)


# ============================================================
# NATURAL BLINK
# ============================================================

def blink():
    eyes.blink()


# ============================================================
# QUICK DOUBLE BLINK
# ============================================================

def double_blink():

    eyes.blink()
    time.sleep(0.06)
    eyes.blink()


# ============================================================
# NATURAL LOOK AROUND
# ============================================================

def look_around():

    direction = random.choice([
        "left",
        "right",
        "up",
        "down",
        "center"
    ])

    if direction == "left":
        look_left()

    elif direction == "right":
        look_right()

    elif direction == "up":
        look_up()

    elif direction == "down":
        look_down()

    else:
        look_center()


# ============================================================
# RANDOM EXPRESSION
# ============================================================

def random_expression():

    expression = random.choice([
        "normal",
        "happy",
        "surprised",
        "angry"
    ])

    eyes.set_expression(expression)


# ============================================================
# TALKING / LISTENING STYLE ANIMATION
# ============================================================

def listening():

    eyes.normal()

    time.sleep(0.3)

    look_left()

    time.sleep(0.25)

    look_right()

    time.sleep(0.25)

    look_center()


# ============================================================
# HAPPY REACTION
# ============================================================

def happy_reaction():

    eyes.happy()

    time.sleep(0.6)

    eyes.normal()


# ============================================================
# SURPRISE REACTION
# ============================================================

def surprise_reaction():

    eyes.surprised()

    time.sleep(0.45)

    eyes.normal()


# ============================================================
# QUICK ANGRY REACTION
# ============================================================

def angry_reaction():

    eyes.angry()

    time.sleep(0.5)

    eyes.normal()


# ============================================================
# STARTUP ANIMATION
# ============================================================

def startup():

    # Start sleeping
    eyes.sleep()

    time.sleep(0.4)

    # Wake up
    eyes.normal()

    time.sleep(0.15)

    # Quick scan
    look_left()
    look_right()
    look_center()

    eyes.blink()


# ============================================================
# IDLE FACE
# ============================================================

def idle():

    # Small random movement
    look_around()

    # Short natural pause
    time.sleep(
        random.uniform(0.25, 0.7)
    )

    # Sometimes blink
    if random.random() < 0.35:

        blink()

        time.sleep(
            random.uniform(0.15, 0.4)
        )

    # Occasionally look back at center
    if random.random() < 0.45:

        look_center()

        time.sleep(
            random.uniform(0.2, 0.5)
        )


# ============================================================
# MAIN
# ============================================================

# try:

#     startup()

#     while True:

#         # ----------------------------------------
#         # Mostly normal idle behavior
#         # ----------------------------------------

#         chance = random.random()


#         # Normal looking around
#         if chance < 0.60:

#             idle()


#         # Happy
#         elif chance < 0.70:

#             happy_reaction()


#         # Quick blink
#         elif chance < 0.82:

#             blink()


#         # Double blink
#         elif chance < 0.88:

#             double_blink()


#         # Surprise
#         elif chance < 0.93:

#             surprise_reaction()


#         # Angry
#         elif chance < 0.96:

#             angry_reaction()


#         # Listening / scanning
#         else:

#             listening()


#         # Very short pause before next action
#         time.sleep(
#             random.uniform(0.08, 0.25)
#         )


# except KeyboardInterrupt:

#     print("\nRobot face stopped.")


# finally:

#     eyes.close()
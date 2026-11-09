import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'yeux'))

import threading, queue, random, time
from robot_eyes_engine_py import RobotEyes
from robot_face_py import *
from config import tapis, réponse_finie
import config
from cerveau import réponses_en_phrases
from voix import dire_cartesia
from oreille import interruption

eyes = RobotEyes(rotation=90)

fil_écoute = threading.Thread(target=interruption)
fil_écoute.start()

startup()

while True:

    try:
        ecrit = tapis.get(timeout=0.1)
    except queue.Empty:
        chance = random.random()
        if chance < 0.60:
            idle()
        elif chance < 0.70:
            happy_reaction()
        elif chance < 0.82:
            blink()
        elif chance < 0.88:
            double_blink()
        elif chance < 0.93:
            surprise_reaction()
        elif chance < 0.96:
            angry_reaction()
        continue

    print(f"[t_reçu_tapis] {time.time():.3f}")
    print(f"[entendu] {ecrit}")

    if not ecrit:
        continue

    réponses_en_phrases(ecrit)

    while not tapis.empty():
        tapis.get()

    while True:

        try:
            ecrit = tapis.get(timeout=0.1)
        except queue.Empty:
            chance = random.random()
            if chance < 0.60:
                idle()
            elif chance < 0.70:
                happy_reaction()
            elif chance < 0.82:
                blink()
            elif chance < 0.88:
                double_blink()
            elif chance < 0.93:
                surprise_reaction()
            elif chance < 0.96:
                angry_reaction()
            continue

        print(f"[t_reçu_tapis] {time.time():.3f}")
        print(f"[entendu] {ecrit}")

        if "au revoir" in ecrit.lower():
            dire_cartesia("Au revoir, Monsieur.")
            break

        elif not ecrit:
            break

        else:
            réponses_en_phrases(ecrit)

            while not tapis.empty():
                tapis.get()

    config.mode_écoute = False
    print("[veille] En attente du wake word...")

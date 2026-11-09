from openwakeword.model import Model
import sounddevice
import numpy
import os

model_path = os.path.join(os.path.dirname(__import__('openwakeword').__file__), 'resources', 'models', 'hey_jarvis_v0.1.onnx')
wakeword = Model(wakeword_model_paths=[model_path])

stream = sounddevice.InputStream(samplerate=16000, channels=1, dtype='int16', device=4)
stream.start()

print("Dis 'Hey Jarvis' dans le micro...")

while True :
    bloc, _ = stream.read(1280)
    audio = bloc[:, 0].astype(numpy.int16)
    prediction = wakeword.predict(audio)
    score = list(prediction.values())[0]
    if score > 0.1 :
        print(f"hey_jarvis: {score:.4f}", end="\r")
    if score > 0.5 :
        print(f"\n>>> WAKE WORD DÉTECTÉ ! (score: {score:.4f})")

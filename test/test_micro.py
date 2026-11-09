import sounddevice, numpy, wave
import subprocess

print('Enregistrement')

freq = 16000
durée = 3

enregistrement = sounddevice.rec(int (durée * freq), samplerate=freq, channels=1, dtype='int16')
sounddevice.wait() # Pas besoin de sounddevice.stop() parce que wait() attend déjà la fin de l'enregistrement
print('Terminé')

with wave.open("test_micro.wav", "wb") as fichieraudio : 
    contenu = fichieraudio.read() # Tentative de compréhension de ce "with"
fichieraudio.setnchannels(1)
fichieraudio.setsampwidth(2)
fichieraudio.setframerate(16000)
fichieraudio.writeframes(enregistrement.tobytes())
fichieraudio.close()

subprocess.run(['paplay', 'test_micro.wav'])
sounddevice.get_stream
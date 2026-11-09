import os, threading, numpy, sounddevice, torch, time
from cartesia import Cartesia
from silero_vad import load_silero_vad
from openwakeword.model import Model
from config import CARTESIA_API_KEY, SAMPLE_RATE_STT, DEVICE_MICRO, WAKEWORD_SEUIL, VAD_SEUIL, SILENCE_MAX, ATTENTE_INITIALE_MAX, tapis, réponse_finie
import config

vad_model, _ = torch.hub.load('snakers4/silero-vad', 'silero_vad')
wakeword_model_path = os.path.join(os.path.dirname(__import__('openwakeword').__file__), 'resources', 'models', 'hey_jarvis_v0.1.onnx')
wakeword = Model(wakeword_model_paths=[wakeword_model_path])

def capter_phrase(stream):
    vad_model.reset_states()
    stt_client = Cartesia(api_key=CARTESIA_API_KEY)
    transcript = ""
    envoyé = 0
    silence = 0
    stt_fini = False

    with stt_client.stt.auto_finalize.websocket(
        model="ink-2",
        encoding="pcm_s16le",
        sample_rate=SAMPLE_RATE_STT,
    ) as ws:
        print("[websocket ouvert]")

        turn_en_cours = ""

        def écouter_events():
            nonlocal transcript, stt_fini, turn_en_cours
            for event in ws:
                if event.type == "turn.update":
                    turn_en_cours = event.transcript or turn_en_cours
                    print(f"[stt update] {turn_en_cours}")
                elif event.type == "turn.end":
                    turn_en_cours = event.transcript or turn_en_cours
                    transcript += " " + turn_en_cours if transcript else turn_en_cours
                    print(f"[stt end] {transcript}")
                    turn_en_cours = ""
                    stt_fini = True
                elif event.type == "error":
                    print(f"[stt error] {event.message}")

        fil_stt = threading.Thread(target=écouter_events, daemon=True)
        fil_stt.start()

        attente_initiale = 0
        while True:
            bloc, _ = stream.read(512)
            tensor = torch.from_numpy(bloc[:, 0].copy()).float() / 32768.0
            score = vad_model(tensor, SAMPLE_RATE_STT).item()
            print(f"[vad] {score:.2f}")

            if score > VAD_SEUIL:
                ws.send_raw(bloc[:, 0].astype(numpy.int16).tobytes())
                envoyé += 1
                silence = 0
                stt_fini = False

            elif envoyé > 10:
                ws.send_raw(bloc[:, 0].astype(numpy.int16).tobytes())
                silence += 1
                if stt_fini or silence > SILENCE_MAX:
                    break

            elif envoyé == 0:
                attente_initiale += 1
                if attente_initiale > ATTENTE_INITIALE_MAX:
                    print("[stt timeout] pas de voix détectée, fermeture")
                    break

        print(f"[envoyé: {envoyé}, silence: {silence}]")
        fil_stt.join(timeout=5)
        if not transcript and turn_en_cours:
            transcript = turn_en_cours
        print(f"[transcript final] {transcript}")
        print(f"[t_stt_fin] {time.time():.3f}")

    return transcript

def interruption():
    stream = sounddevice.InputStream(samplerate=SAMPLE_RATE_STT, channels=1, dtype='int16', device=DEVICE_MICRO)
    stream.start()

    while True:
        if not config.mode_écoute:
            bloc, _ = stream.read(1280)
            audio_ww = bloc[:, 0].astype(numpy.int16)
            prediction = wakeword.predict(audio_ww)
            score_ww = list(prediction.values())[0]
            print(f"score_ww: {score_ww}", end="\r")
            if score_ww > WAKEWORD_SEUIL:
                config.mode_écoute = True
                wakeword.reset()
                print("[wake word détecté]")
                transcript = capter_phrase(stream)
                réponse_finie.clear()
                print(f"[t_avant_tapis] {time.time():.3f}")
                tapis.put(transcript)

        else:
            réponse_finie.wait()
            transcript = capter_phrase(stream)
            réponse_finie.clear()
            print(f"[t_avant_tapis] {time.time():.3f}")
            tapis.put(transcript)

# =============================================
# ANCIENS CODES (trace des essais précédents)
# =============================================

## Exercice 1 — premier chatbot statique

# réponses = {
#     "bonjour": "Bonjour Monsieur.",
#     "ça va": "Toujours opérationnel, Monsieur.",
#     "quelle heure est-il": "Je n'ai pas encore accès à l'horloge, Monsieur.",
#     "qui es-tu": "Je suis Jarvis, votre assistant personnel.",
#     "merci": "À votre service, Monsieur.",
#     "raconte une blague": "Je suis un assistant, pas un humoriste, Monsieur.",
#     "quel temps fait-il": "Je ne suis pas encore connecté à la météo, Monsieur.",
#     "aide": "Je peux répondre à quelques phrases simples pour le moment.",
#     "comment tu vas": "Mes systèmes sont pleinement fonctionnels, Monsieur.",
#     "bonne nuit": "Bonne nuit, Monsieur. Je reste en veille.",
# }
# while True :
#     écoute = input('Dites moi monsieur ?')
#     écoutelower = écoute.lower().strip()
#     if écoutelower == 'au revoir':
#         print("À plus tard Monsieur")
#         break
#     elif écoutelower in réponses :
#         print(réponses[écoutelower])
#     else :
#         print("Je n'ai pas très bien compris Monsieur")

## Premier appel Claude (non-streaming)

# def demander_à_claude(question) :
#     historique.append({"role": "user", "content": question})
#     textedeclaude = claude.messages.create(
#         model="claude-haiku-5-5",
#         max_tokens=200,
#         system=système,
#         messages=historique
#     )
#     reponsedeclaude = textedeclaude.content[0].text
#     historique.append({"role": "assistant", "content": reponsedeclaude})
#     return reponsedeclaude

## TTS Piper (remplacé par Cartesia)

# def dire_piper(reponsedeclaude) :
#     piper = subprocess.run(
#         ["./piper/piper", "--model", "./voix/fr_FR-tom-medium.onnx", "--output_file", "réponse.wav"],
#         input=reponsedeclaude, text=True,
#         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#     lirepiper = subprocess.run(["paplay", "réponse.wav"],
#         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

## STT Whisper (remplacé par Cartesia ink-2)
# from faster_whisper import WhisperModel
# whispermodel = WhisperModel("base", compute_type="int8")

## STT via fichier WAV (remplacé par STT websocket temps réel)

# def transcrire(audio) :
#     with wave.open(audio, "rb") as wav:
#         sample_rate = wav.getframerate()
#         chunks = []
#         while data := wav.readframes(sample_rate // 10):
#             chunks.append(data)
#     transcript = ""
#     with client.stt.auto_finalize.websocket(
#         model="ink-2", encoding="pcm_s16le", sample_rate=sample_rate,
#     ) as ws:
#         for chunk in chunks:
#             ws.send_raw(chunk)
#             time.sleep(0.1)
#         ws.send({"type": "close"})
#         turn_text = ""
#         for event in ws:
#             if event.type == "turn.update":
#                 turn_text = event.transcript or turn_text
#             elif event.type == "turn.end":
#                 transcript += event.transcript or turn_text
#                 turn_text = ""
#     return transcript

## Écoute VAD + enregistrement fichier (remplacé par capter_phrase temps réel)

# def écouter() :
#     stream = sounddevice.InputStream(samplerate=16000, channels=1, dtype='int16', device=13)
#     stream.start()
#     enregistrement = []
#     silence = 0
#     while True :
#         bloc, _ = stream.read(512)
#         tensor = torch.from_numpy(bloc[:, 0].copy()).float() / 32768.0
#         score = vad_model(tensor, 16000).item()
#         if score > 0.9 :
#             enregistrement.append(bloc.copy())
#             silence = 0
#         elif len(enregistrement) > 0 :
#             enregistrement.append(bloc.copy())
#             silence += 1
#             if silence > 15 :
#                 break
#     stream.stop()
#     stream.close()
#     if not enregistrement :
#         return None
#     audio = numpy.concatenate(enregistrement)
#     fichier = "écoute_temp.wav"
#     with wave.open(fichier, 'wb') as f :
#         f.setnchannels(1)
#         f.setsampwidth(2)
#         f.setframerate(16000)
#         f.writeframes(audio.tobytes())
#     return fichier

## Ancien main loop (avant tapis.get(timeout=0.1))

# while True :
#     fichier = tapis.get()
#     ecrit = transcrire(fichier)
#     réponses_en_phrases(ecrit)
#     while not tapis.empty() :
#         tapis.get()

## Animation dans animation() (déplacée dans le main loop)

#     while True :
#         if continuer == True :
#             chance = random.random()
#             if chance < 0.60: idle()
#             elif chance < 0.70: happy_reaction()
#             elif chance < 0.82: blink()
#             elif chance < 0.88: double_blink()
#             elif chance < 0.93: surprise_reaction()
#             elif chance < 0.96: angry_reaction()
#         else :
#             time.sleep(0.1)

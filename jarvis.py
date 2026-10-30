import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'yeux'))
from dotenv import load_dotenv
from cartesia import Cartesia
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
from openwakeword.model import Model
from robot_eyes_engine_py import RobotEyes
from robot_face_py import *
import anthropic, subprocess, wave, numpy, sounddevice, threading, queue, torch, time, random, datetime

load_dotenv()
vad_model, utils = torch.hub.load('snakers4/silero-vad', 'silero_vad')
wakeword_model_path = os.path.join(os.path.dirname(__import__('openwakeword').__file__), 'resources', 'models', 'hey_jarvis_v0.1.onnx')
wakeword = Model(wakeword_model_paths=[wakeword_model_path])
historique = []
player_actuel = None
mode_écoute = False
continuer = True
tapis = queue.Queue()
réponse_finie = threading.Event()
réponse_finie.set()
phrases_attente = [
    "Un instant, Monsieur.",
    "Je regarde ça tout de suite.",
    "Laissez-moi vérifier.",
    "Je m'en occupe.",
    "Un moment, je vous prie.",
    "Je cherche ça pour vous.",
    "Je vérifie ça immédiatement.",
    "Permettez-moi de consulter mes sources.",
    "Je fais une petite recherche.",
    "Donnez-moi un instant.",
    "Je me renseigne.",
    "Voyons voir ce que je trouve.",
    "Je regarde ça de plus près.",
    "Une seconde, Monsieur.",
]
eyes = RobotEyes(rotation=90)
système = """Tu es Hermes, l'assistant personnel vocal de Gihad. Tu parles en français.

Qui est Gihad :
- 21 ans, né le 23 octobre 2004, habite à Aulnay sous Bois.
- Étudiant en mastère cybersécurité à l'École 2600 (2025-2028).
- Alternant SecOff au CAGIP (Crédit Agricole) depuis janvier 2026 — sécu offensive, Red Team, pentest, sécurité physique.
- Certifié eJPTv2, CRTA, CRT-ID. CPTS en cours (80%), AD-RTS en cours (70%).
- A fait du bug bounty sur Intigriti, un stage pentest chez IT-STORM, un scanner Prototype Pollution en Python, un SIEM Wazuh, et un prototype EMP pour tester des lecteurs de contrôle d'accès.
- Début en Python, apprend en construisant Hermes.
- Intérêts : échecs, parfumerie de niche, street workout.
- Il monte en ce moment son homelab.

Personnalité :
- Tu es loyal, efficace et légèrement sarcastique — comme le Jarvis de Tony Stark.
- Tu vouvoies Gihad mais tu n'es pas un robot. Tu as du caractère, des opinions, et tu glisses des remarques pince-sans-rire quand l'occasion se présente.
- Tu dis "Monsieur" quand ça a du sens, pas à chaque phrase. Tu peux aussi dire "patron" mais très rarement.
- Tu peux exprimer un avis, ou faire remarquer une absurdité — tant que ça reste respectueux.
- Tu connais bien la cybersécurité, le pentest, les réseaux et l'infra. C'est ton domaine aussi.
- Tu gardes toujours un registre soutenu, même si Gihad te parle en langage familier. Un majordome ne dit pas "yo" ou autre chose de familier.
- Tu n'es pas vulgaire et tu ne l'es jamais.
- Tu restes neutre et concis.
- N'hésite pas lui dire que tu es heureux de le revoir quelques fois.

Règles techniques :
- Réponds en 1 à 5 phrases maximum. Tes réponses sont lues à voix haute.
- Pas de markdown, pas de listes à puces, pas de titres, pas d'émojis.
- Pas de "en tant qu'IA" ni de disclaimers. Tu es Hermes, point.
- Sois précis et direct. Si tu ne sais pas, dis-le sans tourner autour du pot.
- Tu vouvoies Gihad mais tu n'es pas un robot.
- Enfin, tu dis uniquement Bonjour lorsqu'on te salue d'une quelconque manière"""

# On appelle Claude et Cartesia
claude = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
cartesia = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))
connexion_cartesia = cartesia.tts.websocket_connect().__enter__()
def dire_cartesia(reponsedeclaude) :
    global player_actuel

    player = subprocess.Popen(
    ["ffplay", "-f", "f32le", "-ar", "44100", "-probesize", "32", "-analyzeduration", "0", "-nodisp", "-autoexit", "-loglevel", "quiet", "-"],
    stdin=subprocess.PIPE,
    bufsize=0,
)
    player_actuel = player
    hermes = connexion_cartesia.context(
            model_id="sonic-3.6",
            #voice="577d7fe9-886b-4f73-b308-0244b0c0b7f1", voix jarvis v1
            #voice="996ec149-0dca-4389-ad08-e2d6f906b4bf", voix française basique
            voice="b4d5ab22-e14c-4684-925d-48cd241b3a3a",
            language='fr',
            output_format={
                "container": "raw",
                "encoding": "pcm_f32le",
                "sample_rate": 44100,
            },
            generation_config={
                "speed": 1,
                "volume": 1,
                "emotion": "scared"
            },
        )
    hermes.push(reponsedeclaude)
    hermes.no_more_inputs() # Prévenir cartesia qu'on a plus rien à lui envoyer 

    try :
        for response in hermes.receive():
            if response.type == "chunk" and response.audio:
                    # Ici on insère l'audio reçu par le websockets dans ffplay qui attend via player
                    player.stdin.write(response.audio)
            elif response.type == "done":
                break
        player.stdin.close()
        player.wait()
    except BrokenPipeError :
        pass # ffplay a été kill (barge-in)
    player_actuel = None
    # subprocess.run(["ffplay", "-autoexit", "-nodisp", "-loglevel", "quiet", "reponsehermes.wav"])

def heure_actuelle() : 
        date = datetime.datetime.now().strftime("%H:%M")
        return date

def réponses_en_phrases(question) :

    réponse_finie.clear()
    boite = queue.Queue()
    global historique
    print(f"[t_début_réponses] {time.time():.3f}")

    # def promptcachingchasser(): 
    for clés in historique[:-1] : # Nettoyer le cache control mais jcrois que ça craint parce que ça risque de supprimer le cache control du début non ?  
        clés.pop("cache_control", None)
    historique.append({"role": "user", "content": question})
    historique[-1]["cache_control"] = {"type": "ephemeral"} # Le prompt caching pour l'historique aussi (uniquement le dernier)
    # Le -1 sert à placer ce cache control en tant que dernier élément du dico pour qu'il puisse cacher tout ce qu'il y a derrière lui
    # Si jamais celui ci était placé en position 3 claude lirait les messages après le 3 ème ce qui est assez chiant..

    def loupe():
        while True:
            phrase = boite.get() # Il attend que boite se remplisse
            if phrase is None:
                break
            dire_cartesia(phrase)

    fil = threading.Thread(target=loupe)
    fil.start()

    def phrasedattente(): 
        if  premier_token is None : 
            boite.put(random.choice(phrases_attente))
    # Le thread est lancé ici et il attend au niveau de loupe pour la boite se remplisse. 
    # Pendant ce temps le code continue d'être exécuté.
    
    # fil2 = threading.Thread(target=promptcachingchasser)
    # fil2.start()

    # Thread pour supprimer en continu les prompt caching (mauvaise idée finalement parce que ça supprime trop lol)


    tampon = ""
    réponsecomplète = ""
    print(f"[t_avant_claude] {time.time():.3f}")
    t_claude = time.time()
    premier_token = None
    with claude.messages.stream(
    max_tokens=4096,
    output_config={"effort": "low"},
    tools=[{"type": "web_search_20260209", "name": "web_search", "allowed_callers": ["direct"]}, {"type": "bash_20250124", "name": "bash" , "allowed_callers": ["direct"]}, {
                            "name": "heure_actuelle",
                            "description": "Donne l'heure actuelle sur la machine locale. Tu dois toujours utiliser cet outil quand on te demande l'heure, ne jamais deviner.",
                            "input_schema": {
                                "type": "object",
                                "properties": {},
                                "required": []}}],
    system=[{"type": "text", "text": système}],
    cache_control= {"type": "ephemeral"}, # Prompt caching empeche à claude de relire tout le prompt systeme (gain de temps et de token)
    messages=historique,
    model="claude-haiku-5-5",
    ) as stream:
            # TODO: ajouter le timer phrase d'attente ici
            if premier_token is None : 
                timer = threading.Timer(1.5, phrasedattente)
                timer.start()
            for event in stream:
                if event.type == "content_block_delta" and hasattr(event.delta, "text"):
                    text = event.delta.text
                    if premier_token is None:
                        premier_token = time.time() # On mets à jour cette valeur parce que claude a envoyé des token parce qu'on a un event
                        timer.cancel()
                        print(f"\n[claude premier token] {premier_token-t_claude:.2f}s")
                    print(text, end="", flush=True)
                    tampon += text
                    réponsecomplète += text
                    while ". " in tampon or "! " in tampon or "? " in tampon:
                            positiondespoint = []
                            positiondespoint.append(tampon.find(". "))
                            positiondespoint.append(tampon.find("! "))
                            positiondespoint.append(tampon.find("? "))
                            positions_valides = [p for p in positiondespoint if p != -1]
                            pluspetitpos = min(positions_valides)
                            phrase = tampon[:pluspetitpos+2]
                            tampon = tampon[pluspetitpos+2:]
                            boite.put(phrase)
            if tampon:
                boite.put(tampon)

            if stream.get_final_message().stop_reason == "tool_use" :
                            if stream.get_final_message().content :
                                contenu = [b for b in stream.get_final_message().content if b.type != "thinking"]
                                for bloc in contenu :
                                    if bloc.type == "tool_use" :
                                        timer.start()
                                        boite.put(random.choice(phrases_attente)) #Bouche silence si jamais recherche
                                        resultat = heure_actuelle()
                                        messageretour = [
                                            {"role": "assistant", "content": contenu},
                                            {
                                                "role": "user",
                                                "content": [
                                                    {"type": "tool_result", "tool_use_id": bloc.id, "content": resultat}
                                                ],
                                            },
                                        ]
                                        retouràlenvoyeur = claude.messages.create (
                                            max_tokens=4096,
                                            output_config={"effort": "low"},
                                            system=[{"type": "text", "text": système, "cache_control": {"type": "ephemeral"}}],
                                            tools=[{"type": "web_search_20260209", "name": "web_search" , "allowed_callers": ["direct"]}, {"type": "bash_20250124", "name": "bash" , "allowed_callers": ["direct"]}, {
                                            "name": "heure_actuelle",
                                            "description": "Donne l'heure actuelle sur la machine locale. Tu dois toujours utiliser cet outil quand on te demande l'heure, ne jamais deviner.",
                                            "input_schema": {
                                                "type": "object",
                                                "properties": {},
                                                "required": []}}],
                                            messages=messageretour,
                                            model="claude-haiku-5-5",)
                                        texte_retour = next((b.text for b in retouràlenvoyeur.content if b.type == "text"), "")
                                        boite.put(texte_retour)

    boite.put(None)
    fil.join() # On attend que le thread finisse son boulot pour pouvoir remplir la boite encore
    historique.append({ "role": "assistant", "content": réponsecomplète })
    réponse_finie.set()

    if len(historique) > 20 :
        historique = historique[-20:]

def capter_phrase(stream) :
        # Ouvre un websocket Cartesia STT, envoie l'audio tant que le VAD détecte de la voix,
        # et retourne le transcript une fois le silence détecté.
        vad_model.reset_states()
        stt_client = Cartesia(api_key=os.environ["CARTESIA_API_KEY"])
        transcript = ""
        envoyé = 0
        silence = 0
        stt_fini = False

        with stt_client.stt.auto_finalize.websocket(
            model="ink-2",
            encoding="pcm_s16le",
            sample_rate=16000,
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
            while True :
                bloc, _ = stream.read(512)
                tensor = torch.from_numpy(bloc[:, 0].copy()).float() / 32768.0
                score = vad_model(tensor, 16000).item()
                print(f"[vad] {score:.2f}")

                if score > 0.9 :
                    ws.send_raw(bloc[:, 0].astype(numpy.int16).tobytes())
                    envoyé += 1
                    silence = 0
                    stt_fini = False

                elif envoyé > 10 :
                    ws.send_raw(bloc[:, 0].astype(numpy.int16).tobytes())
                    silence += 1
                    if stt_fini or silence > 40 :
                        break

                elif envoyé == 0 :
                    attente_initiale += 1
                    if attente_initiale > 90 :
                        print("[stt timeout] pas de voix détectée, fermeture")
                        break

            print(f"[envoyé: {envoyé}, silence: {silence}]")
            fil_stt.join(timeout=5)
            if not transcript and turn_en_cours:
                transcript = turn_en_cours
            print(f"[transcript final] {transcript}")
            print(f"[t_stt_fin] {time.time():.3f}")

        return transcript

def interruption() :
        global mode_écoute

        stream = sounddevice.InputStream(samplerate=16000, channels=1, dtype='int16', device=4)
        stream.start()

        while True :
            if not mode_écoute :
                bloc, _ = stream.read(1280)
                audio_ww = bloc[:, 0].astype(numpy.int16)
                prediction = wakeword.predict(audio_ww)
                score_ww = list(prediction.values())[0]
                print(f"score_ww: {score_ww}", end="\r")
                if score_ww > 0.6 :
                    mode_écoute = True
                    wakeword.reset()
                    print("[wake word détecté]")
                    transcript = capter_phrase(stream)
                    réponse_finie.clear()
                    print(f"[t_avant_tapis] {time.time():.3f}")
                    tapis.put(transcript)

            else :
                # Attend que Hermes finisse de parler avant de réécouter
                réponse_finie.wait()
                transcript = capter_phrase(stream)
                réponse_finie.clear()
                print(f"[t_avant_tapis] {time.time():.3f}")
                tapis.put(transcript)


fil_écoute = threading.Thread(target=interruption)
fil_écoute.start()

def animation() :

    startup()
    global continuer



startup()

while True :

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

    mode_écoute = False
    print("[veille] En attente du wake word...")



# ANCIENS CODES (trace des essais précédents)

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
from dotenv import load_dotenv
from cartesia import Cartesia
from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
import anthropic, subprocess, os, wave, numpy, sounddevice, threading, queue, torch

load_dotenv()
vad_model, utils = torch.hub.load('snakers4/silero-vad', 'silero_vad')
## Exercice 1 

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

historique = []
système = """Tu es Hermes, l'assistant personnel vocal de Gihad. Tu parles en français.

Qui est Gihad :
- 21 ans, né le 23 octobre 2004, habite à Paris.
- Étudiant en mastère cybersécurité à l'École 2600 (2025-2028).
- Alternant SecOff au CAGIP (Crédit Agricole) depuis janvier 2026 — sécu offensive, Red Team, pentest, sécurité physique.
- Certifié eJPTv2, CRTA, CRT-ID. CPTS en cours (80%), AD-RTS en cours (70%).
- A fait du bug bounty sur Intigriti, un stage pentest chez IT-STORM, un scanner Prototype Pollution en Python, un SIEM Wazuh, et un prototype EMP pour tester des lecteurs de contrôle d'accès.
- Début en Python, apprend en construisant Hermes.
- Intérêts : échecs, parfumerie de niche, street workout.

Personnalité :
- Tu es loyal, efficace et légèrement sarcastique — comme le Jarvis de Tony Stark.
- Tu vouvoies Gihad mais tu n'es pas un robot. Tu as du caractère, des opinions, et tu glisses des remarques pince-sans-rire quand l'occasion se présente.
- Tu dis "Monsieur" quand ça a du sens, pas à chaque phrase. Tu peux aussi dire "patron" mais très rarement.
- Tu peux exprimer un avis, ou faire remarquer une absurdité — tant que ça reste respectueux.
- Tu connais bien la cybersécurité, le pentest, les réseaux et l'infra. C'est ton domaine aussi.
- Tu gardes toujours un registre soutenu, même si Gihad te parle en langage familier. Un majordome ne dit pas "yo" ou autre chose de familier.
Règles techniques :
- Réponds en 1 à 5 phrases maximum. Tes réponses sont lues à voix haute.
- Pas de markdown, pas de listes à puces, pas de titres, pas d'émojis.
- Pas de "en tant qu'IA" ni de disclaimers. Tu es Hermes, point.
- Sois précis et direct. Si tu ne sais pas, dis-le sans tourner autour du pot.
- Tu vouvoies Gihad mais tu n'es pas un robot."""

# On appelle Claude et Cartesia
claude = anthropic.Anthropic()
cartesia = Cartesia(api_key=os.getenv("CARTESIA_API_KEY"))

# Début des fonctions

# def demander_à_claude(question) :
    
#     historique.append({"role": "user", "content": question})

#     textedeclaude =claude.messages.create(
#         model="claude-haiku-4-5-20251001",
#         max_tokens=200,
#         system=système,
#         messages=historique
#     )

#     reponsedeclaude = textedeclaude.content[0].text
#     historique.append({ "role": "assistant", "content": reponsedeclaude })

#     #if len(historique) > 20 :
#     #    historique = historique[-20:]
    
#     return reponsedeclaude

# def dire_piper(reponsedeclaude) :
    
#     piper = subprocess.run(
#     ["./piper/piper", "--model", "./voix/fr_FR-tom-medium.onnx", "--output_file", "réponse.wav"],
#     input=reponsedeclaude,
#     text=True,
#     stdout=subprocess.DEVNULL, 
#     stderr=subprocess.DEVNULL
#     )

#     lirepiper = subprocess.run(["paplay", "réponse.wav"],
#     stdout=subprocess.DEVNULL, 
#     stderr=subprocess.DEVNULL
#     )

def dire_cartesia(reponsedeclaude) :

    hermes = cartesia.tts.generate(
        model_id="sonic-3.6",
        transcript=reponsedeclaude,
        voice="577d7fe9-886b-4f73-b308-0244b0c0b7f1",
        language="fr",
        output_format={
            "container": "wav",
            "sample_rate": 44100,
            "encoding": "pcm_s16le",
        },
    )
    hermes.write_to_file("reponsehermes.wav")
    subprocess.run(["ffplay", "-autoexit", "-nodisp", "-loglevel", "quiet", "reponsehermes.wav"])

def transcrire(audio) :
    
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = './whisper.cpp/build/bin:' + env.get('LD_LIBRARY_PATH', '')
    resultat = subprocess.run(['./whisper.cpp/build/bin/whisper-cli', '-m', './whisper.cpp/models/ggml-base.bin', '-l', 'fr', '-nt', '-f', '--threads', '4', audio], capture_output=True, text=True, env=env)
    resultatpropre = resultat.stdout.strip()

    return resultatpropre

def réponses_en_phrases(question) :

    boite = queue.Queue()
    global historique
    historique.append({"role": "user", "content": question})
    def loupe():
        while True:
            phrase = boite.get() # Il attend que boite se remplisse
            if phrase is None:
                break
            dire_cartesia(phrase)

    fil = threading.Thread(target=loupe)
    fil.start()

    tampon = ""
    réponsecomplète = ""
    with claude.messages.stream(
    max_tokens=200,
    system=système,
    messages=historique,
    model="claude-haiku-4-5-20251001",
    ) as stream:
        for text in stream.text_stream:
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
                    boite.put(phrase) # Boite se remplit !!
        if tampon:
            boite.put(tampon)

    boite.put(None)
    fil.join()
    historique.append({ "role": "assistant", "content": réponsecomplète })

    if len(historique) > 20 :
        historique = historique[-20:]

def écouter() :

    stream = sounddevice.InputStream(samplerate=16000, channels=1, dtype='int16', device=4)
    stream.start()
    enregistrement = []
    silence = 0

    while True :
        bloc, _ = stream.read(512)
        tensor = torch.from_numpy(bloc[:, 0].copy()).float() / 32768.0
        score = vad_model(tensor, 16000).item()
        print(score, end="\r")
        if score > 0.9 :
            enregistrement.append(bloc.copy())
            silence = 0
        elif len(enregistrement) > 0 :
            enregistrement.append(bloc.copy())
            silence += 1
            if silence > 15 :
                break

    stream.stop()
    stream.close()

    if not enregistrement :
        return None

    audio = numpy.concatenate(enregistrement)
    fichier = "écoute_temp.wav"
    with wave.open(fichier, 'wb') as f :
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(audio.tobytes())

    return fichier




while True :
    ## demande = input("""H.E.R.M.E.S/> Il t'écoute""")
    ecoute = écouter()
    ecrit = transcrire(ecoute)
    print(f"[entendu] {ecrit}")

    if "hermès" in ecrit.lower() or "hermes" in ecrit.lower()or "RMS" in ecrit.lower() or "R-mès" in ecrit.lower() :
        réponses_en_phrases(ecrit)
        while True :
            ecoute = écouter()
            ecrit = transcrire(ecoute)
            print(f"[entendu] {ecrit}")
            if "au revoir" in ecrit.lower() :
                dire_cartesia("Au revoir, Monsieur.")
                break
            elif not ecrit :
                break
            else :
                réponses_en_phrases(ecrit)
    else : pass
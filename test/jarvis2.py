import os, sys, time, wave, subprocess, threading, queue, numpy
import sounddevice as sd 
from cartesia import Cartesia
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
jarvis = Cartesia(api_key = os.getenv("CARTESIA-API-KEY")) # os.getenv pour aller chercher la variable dans le .env
ia = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
historique = []
systeme = """Tu es Hermes, l'assistant personnel vocal de Gihad. Tu parles en français.

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
- Tu n'es pas vulgaire et tu ne le sera jamais.
- Tu restes neutre et concis.
- N'hésite pas lui dire que tu es heureux de le revoir quelques fois.

Règles techniques :
- Réponds en 1 à 5 phrases maximum. Tes réponses sont lues à voix haute.
- Pas de markdown, pas de listes à puces, pas de titres, pas d'émojis.
- Pas de "en tant qu'IA" ni de disclaimers. Tu es Hermes, point.
- Sois précis et direct. Si tu ne sais pas, dis-le sans tourner autour du pot.
- Tu vouvoies Gihad mais tu n'es pas un robot.
- Tu ne l'appelles jamais par son prénom.
- Enfin, tu dis uniquement Bonjour lorsqu'on te salue d'une quelconque manière"""


def haiku(q) :
    global historique
    reponsedeclaude = ""

    with ia.messages.stream(
        max_tokens=200,
        messages=historique,
        model='claude-haiku-5-5',
        system=systeme
    ) as stream : 
            for text in stream.text_stream:
                reponsedeclaude += text
                q.put(text)
                print(text, end="", flush=True)

    q.put(None)
    historique.append({"role": "assistant", "content": reponsedeclaude})

def dire_jarvis(q):

    print("ffplay commence à lire ton audio...") # ?

    lecteur = subprocess.Popen(["ffplay", "-f", "f32le", "-ar", "44100", "-probesize", "32", "-analyzeduration", "0", "-nodisp", "-autoexit", "-loglevel", "quiet", "-"],
    stdin=subprocess.PIPE, # Tuyau crée en attente de données texte
    bufsize=0,
    )

    # Connexion à cartesia

    with jarvis.tts.websocket_connect() as connexion:
        cnx = connexion.context(
        model_id="sonic-3.6",
        voice="b4d5ab22-e14c-4684-925d-48cd241b3a3a",
        language="fr",
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

        # Lecture chunk par chunk depuis la queue
        while True:
            chunk = q.get()
            if chunk is None:
                break
            cnx.push(chunk)

        cnx.no_more_inputs()

        for mot in cnx.receive():
            lecteur.stdin.write(mot.audio)

    lecteur.stdin.close()
    lecteur.wait()

def ecoute() : 

    capture = sd.InputStream(samplerate=16000, blocksize=512, channels=1, dtype='int16', device=8)
    sd.start()

    with jarvis.stt.auto_finalize.websocket(
            encoding="pcm_s16le",
            model="ink-2",
            sample_rate=16000,
    ) as connection :
        chunks_byte = (16000 * 2) // 10 
        for chunks in range(0, len(capture), chunks_byte) :
            connection.send_raw(capture[chunks :chunks + chunk_bytes])
            time.sleep(0.1)


    
while True : 

    texte = input('Dit moi ce que tu veux dire à Jarvis')
    historique.append({"role": "user", "content": texte}) # Envoi de la question dans l'historique
    q = queue.Queue()
    t = threading.Thread(target=dire_jarvis, args=(q,))
    t.start()
    haiku(q)
    t.join()

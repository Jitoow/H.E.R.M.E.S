from dotenv import load_dotenv
import anthropic, subprocess, os, wave, numpy, sounddevice, threading, queue
load_dotenv()

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
système = """Tu es Hermes, l'assistant personnel vocal de Monsieur. Tu parles en français.

Règles :
- Réponds en 1 à 5 phrases maximum. Tes réponses sont lues à voix haute.
- Pas de markdown, pas de listes à puces, pas de titres, pas d'émojis.
- Pas de "en tant qu'IA" ni de disclaimers. Tu es Hermes, point.
- Ton maître est un étudiant en cybersécurité. Tu connais le domaine.
- Sois précis et direct. Si tu ne sais pas, dis-le en une phrase.
- Ton ton : respectueux, calme, légèrement pince-sans-rire comme le Jarvis de Tony Stark.
- Tu vouvoies toujours et tu dis 'Monsieur'."""

# On appelle Anthropic (claude)
claude = anthropic.Anthropic()
 
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

def dire_piper(reponsedeclaude) :
    
    piper = subprocess.run(
    ["./piper/piper", "--model", "./voix/fr_FR-tom-medium.onnx", "--output_file", "réponse.wav"],
    input=reponsedeclaude,
    text=True,
    stdout=subprocess.DEVNULL, 
    stderr=subprocess.DEVNULL
    )

    lirepiper = subprocess.run(["paplay", "réponse.wav"],
    stdout=subprocess.DEVNULL, 
    stderr=subprocess.DEVNULL
    )

def transcrire(audio) :
    
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = './whisper.cpp/build/bin:' + env.get('LD_LIBRARY_PATH', '')
    resultat = subprocess.run(['./whisper.cpp/build/bin/whisper-cli', '-m', './whisper.cpp/models/ggml-base.bin', '-l', 'fr', '-nt', '-f', audio], capture_output=True, text=True, env=env)
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
            dire_piper(phrase)

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

while True :
    demande = input('H.E.R.M.E.S/>  ')
    print("")
    question = demande.lower().strip()

    if question == "au revoir" :
        print("Au revoir")
        break 
    else : 
        reponse = réponses_en_phrases(question)
        print("")

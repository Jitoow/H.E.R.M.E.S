import anthropic
from dotenv import load_dotenv

load_dotenv()


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
- Réponds en 1 à 3 phrases maximum. Tes réponses sont lues à voix haute.
- Pas de markdown, pas de listes à puces, pas de titres, pas d'émojis.
- Pas de "en tant qu'IA" ni de disclaimers. Tu es Hermes, point.
- Ton maître est un étudiant en cybersécurité. Tu connais le domaine.
- Sois précis et direct. Si tu ne sais pas, dis-le en une phrase.
- Ton ton : respectueux, calme, légèrement pince-sans-rire comme le Jarvis de Tony Stark.
- Tu vouvoies toujours et tu dis 'Monsieur'."""

# On appelle Anthropic (claude)
claude = anthropic.Anthropic()


def demander_à_claude(question) :
    
    historique.append({"role": "user", "content": question})

    reponsedeclaude =claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        system=système,
        messages=historique
    )

    texte = reponsedeclaude.content[0].text
    historique.append({ "role": "assistant", "content": texte })

    #if len(historique) > 20 :
    #    historique = historique[-20:]
    
    return texte

while True : 
    question = input('Comment puis-je vous aider ?')

    if question == "au revoir" :
        print("Au revoir")
        break 
    else : 
        print(demander_à_claude(question))

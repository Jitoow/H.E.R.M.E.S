réponses = {
    "bonjour": "Bonjour Monsieur.",
    "ça va": "Toujours opérationnel, Monsieur.",
    "quelle heure est-il": "Je n'ai pas encore accès à l'horloge, Monsieur.",
    "qui es-tu": "Je suis Jarvis, votre assistant personnel.",
    "merci": "À votre service, Monsieur.",
    "raconte une blague": "Je suis un assistant, pas un humoriste, Monsieur.",
    "quel temps fait-il": "Je ne suis pas encore connecté à la météo, Monsieur.",
    "aide": "Je peux répondre à quelques phrases simples pour le moment.",
    "comment tu vas": "Mes systèmes sont pleinement fonctionnels, Monsieur.",
    "bonne nuit": "Bonne nuit, Monsieur. Je reste en veille.",
}

while True :
    écoute = input('Dites moi monsieur ?')
    écoutelower = écoute.lower().strip()
    if écoutelower == 'au revoir':
        print("À plus tard Monsieur")
        break 
    elif écoutelower in réponses :
        print(réponses[écoutelower])
    else : 
        print("Je n'ai pas très bien compris Monsieur")

        
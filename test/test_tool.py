import anthropic, datetime
from dotenv import load_dotenv
load_dotenv()
claude = anthropic.Anthropic()


def heure_actuelle() : 
        date = datetime.datetime.now().strftime("%H:%M")
        return date


while True : 

    useruinput = input('Que veux tu dire à claude ? ')

    reponsedeclaude = claude.messages.create(
        max_tokens=200,
        tools=[{
        "name": "heure_actuelle",
        "description": "Donne l'heure actuelle sur la machine locale. Tu dois toujours utiliser cet outil quand on te demande l'heure, ne jamais deviner.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }],
        messages=[{"role": "user", "content": useruinput}],
        model="claude-haiku-4-5-20251001",
        tool_choice={"type": "tool", "name": "heure_actuelle"},
    )

    if reponsedeclaude.stop_reason == "tool_use" :
        if reponsedeclaude.content : 
            contenu = reponsedeclaude.content
            for bloc in reponsedeclaude.content :
                if bloc.type == "tool_use" :
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
                        max_tokens=200,
                        tools=[{"type": "web_search_20260209", "name": "web_search" , "allowed_callers": ["direct"]}, {"type": "bash_20250124", "name": "bash" , "allowed_callers": ["direct"]}, {
                        "name": "heure_actuelle",
                        "description": "Donne l'heure actuelle sur la machine locale. Tu dois toujours utiliser cet outil quand on te demande l'heure, ne jamais deviner.",
                        "input_schema": {
                            "type": "object",
                            "properties": {},
                            "required": []}}], 
                        messages=messageretour,
                        model="claude-haiku-4-5-20251001",)
                    print(retouràlenvoyeur.content[0].text)
    else : 
        print(reponsedeclaude)

import anthropic, queue, threading, time, random, datetime
from config import ANTHROPIC_API_KEY, système, phrases_attente, réponse_finie
import config
from voix import dire_cartesia

claude = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def heure_actuelle():
    return datetime.datetime.now().strftime("%H:%M")

def réponses_en_phrases(question):
    réponse_finie.clear()
    boite = queue.Queue()
    print(f"[t_début_réponses] {time.time():.3f}")

    for clés in config.historique[:-1]:
        clés.pop("cache_control", None)
    config.historique.append({"role": "user", "content": question})
    config.historique[-1]["cache_control"] = {"type": "ephemeral"}

    def loupe():
        while True:
            phrase = boite.get()
            if phrase is None:
                break
            dire_cartesia(phrase)

    fil = threading.Thread(target=loupe)
    fil.start()

    def phrasedattente():
        if premier_token is None:
            boite.put(random.choice(phrases_attente))

    tampon = ""
    réponsecomplète = ""
    print(f"[t_avant_claude] {time.time():.3f}")
    t_claude = time.time()
    premier_token = None
    with claude.messages.stream(
        max_tokens=4096,
        output_config={"effort": "low"},
        tools=[{"type": "web_search_20260209", "name": "web_search", "allowed_callers": ["direct"]}, {"type": "bash_20250124", "name": "bash", "allowed_callers": ["direct"]}, {
            "name": "heure_actuelle",
            "description": "Donne l'heure actuelle sur la machine locale. Tu dois toujours utiliser cet outil quand on te demande l'heure, ne jamais deviner.",
            "input_schema": {
                "type": "object",
                "properties": {},
                "required": []}}],
        system=[{"type": "text", "text": système}],
        cache_control={"type": "ephemeral"},
        messages=config.historique,
        model="claude-haiku-5-5",
    ) as stream:
        if premier_token is None:
            timer = threading.Timer(1.5, phrasedattente)
            timer.start()
        for event in stream:
            if event.type == "content_block_delta" and hasattr(event.delta, "text"):
                text = event.delta.text
                if premier_token is None:
                    premier_token = time.time()
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

        if stream.get_final_message().stop_reason == "tool_use":
            if stream.get_final_message().content:
                contenu = [b for b in stream.get_final_message().content if b.type != "thinking"]
                for bloc in contenu:
                    if bloc.type == "tool_use":
                        boite.put(random.choice(phrases_attente))
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
                        retouràlenvoyeur = claude.messages.create(
                            max_tokens=4096,
                            output_config={"effort": "low"},
                            system=[{"type": "text", "text": système, "cache_control": {"type": "ephemeral"}}],
                            tools=[{"type": "web_search_20260209", "name": "web_search", "allowed_callers": ["direct"]}, {"type": "bash_20250124", "name": "bash", "allowed_callers": ["direct"]}, {
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
    fil.join()
    config.historique.append({"role": "assistant", "content": réponsecomplète})
    réponse_finie.set()

    if len(config.historique) > 20:
        config.historique = config.historique[-20:]

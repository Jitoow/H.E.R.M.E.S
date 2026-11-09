# H.E.R.M.E.S

Mon assistant vocal perso inspiré de Jarvis... en Python.

L'idée c'est un assistant qui écoute, comprend et répond à voix haute... le tout en streaming pour que ça soit fluide.

## Comment ça marche

1. **Wake Word** — OpenWakeWord écoute en boucle... dès qu'il entend "Hey Jarvis" il se réveille
2. **VAD** — Silero VAD détecte quand je parle et quand je m'arrête
3. **STT** — Cartesia ink-2 transcrit ma voix en temps réel via WebSocket... pas besoin d'attendre la fin de la phrase
4. **LLM** — Claude Haiku 5.5 avec prompt caching... il peut chercher sur le web et donner l'heure aussi
5. **TTS** — Cartesia sonic-3.6 en streaming... il commence à parler avant même d'avoir fini de réfléchir

## Les fichiers

```
main.py          → la boucle principale + les animations des yeux
oreille.py       → le micro, wake word, VAD, STT temps réel
cerveau.py       → Claude API, streaming, découpage en phrases, tool use
voix.py          → TTS Cartesia → ffplay via pipe
config.py        → tout ce qui est partagé entre les modules
```

## Le matos

- ReSpeaker pour le micro
- GeeKPi DeskPi RackMate T1... rack 10 pouces 8U
- Écran + miroir sans tain pour l'affichage

## Lancer

```bash
cd IA
source .venv/bin/activate
python3 main.py
```

## Dépendances

- `anthropic` — API Claude
- `cartesia[websockets]` — TTS + STT
- `sounddevice`, `numpy` — capture audio
- `torch`, `silero-vad` — détection vocale
- `openwakeword` — wake word
- `python-dotenv` — variables d'environnement
- `opencv-python`, `Pillow` — les yeux

import subprocess
from cartesia import Cartesia
from config import CARTESIA_API_KEY, SAMPLE_RATE_TTS
import config

cartesia = Cartesia(api_key=CARTESIA_API_KEY)
connexion_cartesia = cartesia.tts.websocket_connect().__enter__()

def dire_cartesia(reponsedeclaude):
    player = subprocess.Popen(
        ["ffplay", "-f", "f32le", "-ar", str(SAMPLE_RATE_TTS), "-probesize", "32", "-analyzeduration", "0", "-nodisp", "-autoexit", "-loglevel", "quiet", "-"],
        stdin=subprocess.PIPE,
        bufsize=0,
    )
    config.player_actuel = player
    hermes = connexion_cartesia.context(
        model_id="sonic-3.6",
        voice="b4d5ab22-e14c-4684-925d-48cd241b3a3a",
        language='fr',
        output_format={
            "container": "raw",
            "encoding": "pcm_f32le",
            "sample_rate": SAMPLE_RATE_TTS,
        },
        generation_config={
            "speed": 1,
            "volume": 1,
            "emotion": "scared"
        },
    )
    hermes.push(reponsedeclaude)
    hermes.no_more_inputs()

    try:
        for response in hermes.receive():
            if response.type == "chunk" and response.audio:
                player.stdin.write(response.audio)
            elif response.type == "done":
                break
        player.stdin.close()
        player.wait()
    except BrokenPipeError:
        pass
    config.player_actuel = None

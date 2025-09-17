import requests
from settings import CONFIG

API_KEY = CONFIG["ELEVEN_API_KEY"]
VOICE_ID = CONFIG["ELEVEN_VOICE_ID"]

HEADERS = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

def gerar_audio(texto: str, output_path: str = "resposta.mp3"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    payload = {
        "text": texto,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.7
        }
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path

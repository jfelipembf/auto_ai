from dotenv import load_dotenv
import os

load_dotenv()

CONFIG = {
    "EVOLUTION_API_URL": os.getenv("EVOLUTION_API_URL"),
    "N8N_URL": os.getenv("N8N_URL"),
    "POSTGRES_URL": os.getenv("POSTGRES_URL"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "OPENAI_MODEL": os.getenv("OPENAI_MODEL"),
    "GOOGLE_CALENDAR_ID": os.getenv("GOOGLE_CALENDAR_ID"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TIMEZONE": os.getenv("TIMEZONE", "America/Maceio"),
    "ELEVEN_API_KEY": os.getenv("ELEVEN_API_KEY"),
    "ELEVEN_VOICE_ID": os.getenv("ELEVEN_VOICE_ID", "EXAVITQu4vr4xnSDxMaL"),
    # Evolution API Auth
    "EVOLUTION_API_KEY": os.getenv("EVOLUTION_API_KEY"),
    "EVOLUTION_INSTANCE": os.getenv("EVOLUTION_INSTANCE")
}

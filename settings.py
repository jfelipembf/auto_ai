from dotenv import load_dotenv
import os

load_dotenv()

CONFIG = {
    "EVOLUTION_API_URL": os.getenv("EVOLUTION_API_URL"),
    "N8N_URL": os.getenv("N8N_URL"),
    # usa POSTGRES_URL; se não houver, tenta DATABASE_URL (Supabase)
    "POSTGRES_URL": os.getenv("POSTGRES_URL") or os.getenv("DATABASE_URL"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "OPENAI_MODEL": os.getenv("OPENAI_MODEL"),
    "OPENAI_TRANSCRIBE_MODEL": os.getenv("OPENAI_TRANSCRIBE_MODEL", "whisper-1"),
    "GOOGLE_CALENDAR_ID": os.getenv("GOOGLE_CALENDAR_ID"),
    "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"),
    "TIMEZONE": os.getenv("TIMEZONE", "America/Maceio"),
    "DEBOUNCE_SECONDS": int(os.getenv("DEBOUNCE_SECONDS", "6")),
    "SYNC_PROCESSING": os.getenv("SYNC_PROCESSING", "false").lower() in ("1", "true", "yes"),
    "ELEVEN_API_KEY": os.getenv("ELEVEN_API_KEY"),
    "ELEVEN_VOICE_ID": os.getenv("ELEVEN_VOICE_ID", "EXAVITQu4vr4xnSDxMaL"),
    # Evolution API Auth
    "EVOLUTION_API_KEY": os.getenv("EVOLUTION_API_KEY"),
    "EVOLUTION_INSTANCE": os.getenv("EVOLUTION_INSTANCE")
}

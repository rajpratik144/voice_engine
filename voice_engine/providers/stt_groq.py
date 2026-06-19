import os
from groq import Groq
from .base import STTProvider

class GroqSTTProvider(STTProvider):
    """
    Ultra-fast, free STT using Groq's Whisper-Large-V3.
    """
    def __init__(self, api_key: str):
        # DO NOT hardcode the key here. 
        # The key is passed in from main.py via load_dotenv()
        self.client = Groq(api_key=api_key)

    async def transcribe(self, audio_file_path: str) -> str:
        """Sends audio to Groq and returns the text."""
        with open(audio_file_path, "rb") as file:
            transcription = self.client.audio.transcriptions.create(
                file=(audio_file_path, file.read()),
                model="whisper-large-v3",
                response_format="text",
                language="en"
            )
        return transcription
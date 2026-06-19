# ==========================================
# File: voice_engine/providers/tts_edge.py
# ==========================================


import edge_tts
from .base import TTSProvider
from typing import AsyncGenerator

class EdgeTTSProvider(TTSProvider):
    """
    A $0-cost TTS Provider using Microsoft Edge's Neural voices.
    Requires no API keys.
    """
    def __init__(self,voice:str="en-US-AndrewNeural"):
        """
        Initialize with a specific neural voice.
        'AndrewNeural' is high-quality and natural.
        """
        self.voice = voice

    async def generate_stream(self, text:str) -> AsyncGenerator[bytes,None]:
        """
        Streams audio data from Microsoft's servers in chunks.
        """
        # Create the communication object with text and voice
        communicate = edge_tts.Communicate(text,self.voice)

        # Iterate over the stream as it arrives from the internet
        async for chunk in communicate.stream():
            # edge-tts returns a dictionary; we only want the audio bytes
            if chunk["type"] == "audio":
                yield chunk["data"]
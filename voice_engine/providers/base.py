from abc import ABC, abstractmethod
from typing import AsyncGenerator

class TTSProvider(ABC):
    """
    Abstract Base Class for Text-to-Speech providers.
    This ensures our system is 'Provider-Agnostic'.
    """

    @abstractmethod
    async def generate_stream(self,text:str)-> AsyncGenerator[bytes,None]:
        """
        An asynchronous generator that yields audio chunks (bytes).
        
        :param text: The string of text to be converted to speech.
        :yield: Chunks of audio data as bytes.
        """
        pass

class STTProvider(ABC):
    """Abstract interface for Speech-to-Text providers."""

    @abstractmethod
    async def transcribe(self, audio_file_path: str) -> str:
        """Should return the transcribed text from an audio file."""
        pass
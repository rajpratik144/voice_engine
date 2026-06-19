# ==========================================
# File: voice_engine/core/ear.py
# ==========================================


import pyaudio
import wave
import os
import time
import audioop # Lightweight math for volume detection
from ..providers.base import STTProvider

class Ear:
    """
    The Ear Module: Handles microphone interaction and Speech-to-Text.
    Stateless and provider-agnostic.
    """
    def __init__(self, provider: STTProvider, config: dict = None):
        """
        Dependency Injection:
        - provider: An instance of an STTProvider (e.g., GroqSTTProvider).
        - config: Hardware and VAD settings.
        """
        self.provider = provider
        
        # Load configuration with safe defaults
        self.config = config or {}
        
        # Hardware Settings
        self.chunk_size = self.config.get("chunk_size", 1024)
        self.format = pyaudio.paInt16
        self.channels = self.config.get("channels", 1)
        self.rate = self.config.get("sample_rate", 16000) # Whisper standard
        
        # VAD (Voice Activity Detection) Settings
        self.silence_threshold = self.config.get("silence_threshold", 1200)
        self.silence_duration = self.config.get("silence_duration", 1.5)
        
        # Internal State
        self.p = pyaudio.PyAudio()
        self.temp_filename = "user_input.wav"

    async def listen(self):
        """
        Listens to the microphone until silence is detected, 
        then transcribes the result via the injected provider.
        """
        stream = self.p.open(
            format=self.format, 
            channels=self.channels,
            rate=self.rate, 
            input=True,
            frames_per_buffer=self.chunk_size
        )

        print("\n[Ear] Listening... (Start speaking)")
        
        frames = []
        silent_chunks = 0
        has_started_talking = False
        
        # Calculate how many silent chunks equal the silence duration
        silence_limit = int(self.silence_duration * (self.rate / self.chunk_size))

        try:
            while True:
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
                
                # Simple VAD: Calculate the volume (RMS) of the chunk
                rms = audioop.rms(data, 2)
                
                if rms > self.silence_threshold:
                    if not has_started_talking:
                        print("[Ear] Heard you! Recording...")
                        has_started_talking = True
                    silent_chunks = 0 # Reset silence timer
                else:
                    if has_started_talking:
                        silent_chunks += 1
                
                # Stop recording once user has finished talking
                if has_started_talking and silent_chunks > silence_limit:
                    print("[Ear] Silence detected. Processing...")
                    break
        finally:
            stream.stop_stream()
            stream.close()

        # 1. Save buffer to temporary file
        self._save_audio(frames)
        
        # 2. Transcribe using the agnostic provider
        text = await self.provider.transcribe(self.temp_filename)
        
        # 3. Clean up the temp file
        if os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)
            
        return text

    def _save_audio(self, frames):
        """Utility to save raw PCM frames to a standard WAV file."""
        wf = wave.open(self.temp_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()

    def is_someone_talking(self, custom_threshold=None):
        """
        Lightweight check to see if current volume is above threshold.
        Supports a custom_threshold to allow barge-in logic to ignore 
        speaker feedback.
        """
        threshold = custom_threshold if custom_threshold is not None else self.silence_threshold
        
        stream = self.p.open(
            format=self.format, 
            channels=self.channels,
            rate=self.rate, 
            input=True,
            frames_per_buffer=self.chunk_size
        )
        try:
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            rms = audioop.rms(data, 2)
            return rms > threshold
        except Exception:
            return False
        finally:
            stream.stop_stream()
            stream.close()
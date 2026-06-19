import pyaudio
import wave
import os
import time
import audioop # Lightweight math for volume detection
from ..providers.base import STTProvider

class Ear:
    def __init__(self, provider: STTProvider, silence_threshold=1000, silence_duration=1.5):
        self.provider = provider
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000 # Standard for Whisper
        self.p = pyaudio.PyAudio()
        
        # VAD Settings
        self.silence_threshold = silence_threshold  # Minimum volume to consider "speech"
        self.silence_duration = silence_duration    # How many seconds of silence to stop
        
        self.temp_filename = "user_input.wav"

    async def listen(self):
        """
        Listens to the microphone until silence is detected, 
        then transcribes the result.
        """
        stream = self.p.open(format=self.format, channels=self.channels,
                            rate=self.rate, input=True,
                            frames_per_buffer=self.chunk_size)

        print("\nListening... (Start speaking)")
        
        frames = []
        silent_chunks = 0
        has_started_talking = False
        
        # Logic: We keep recording as long as the user is talking or 
        # until they have been silent for a specific duration.
        while True:
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            frames.append(data)
            
            # Simple VAD: Calculate the volume (RMS) of the chunk
            rms = audioop.rms(data, 2)
            
            if rms > self.silence_threshold:
                if not has_started_talking:
                    print("Heard you! Recording...")
                    has_started_talking = True
                silent_chunks = 0 # Reset silence timer
            else:
                if has_started_talking:
                    silent_chunks += 1
            
            # If the user has been silent for the duration, stop recording
            silence_limit = int(self.silence_duration * (self.rate / self.chunk_size))
            if has_started_talking and silent_chunks > silence_limit:
                print("Silence detected. Processing...")
                break

        # Stop and close the stream
        stream.stop_stream()
        stream.close()

        # Save to temporary file
        self._save_audio(frames)
        
        # Transcribe
        text = await self.provider.transcribe(self.temp_filename)
        
        # Clean up
        if os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)
            
        return text

    def _save_audio(self, frames):
        """Saves the recorded audio chunks to a WAV file."""
        wf = wave.open(self.temp_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()

    def is_someone_talking(self):
        """Peeks at the mic to see if volume is above threshold."""
        stream = self.p.open(format=self.format, channels=self.channels,
                            rate=self.rate, input=True,
                            frames_per_buffer=self.chunk_size)
        try:
            data = stream.read(self.chunk_size, exception_on_overflow=False)
            rms = audioop.rms(data, 2)
            return rms > self.silence_threshold
        except:
            return False
        finally:
            stream.stop_stream()
            stream.close()
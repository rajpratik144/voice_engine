# ==========================================
# File: voice_engine/core/mouth.py
# ==========================================

import subprocess
import asyncio
import os
import re
from ..providers.base import TTSProvider

class Mouth:
    def __init__(self, provider: TTSProvider):
        self.provider = provider
        self.temp_dir = "temp_audio"
        self._current_process = None
        self._is_interrupted = False
        
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir, exist_ok=True)

    def _clean_text_for_speech(self, text: str) -> str:
        text = re.sub(r'\|?[\s\-]*[\-:]{3,}[\s\- |]*', ' ', text)
        text = text.replace("|", " ").replace("**", "").replace("*", "").replace("#", "")
        text = re.sub(r'^\s*[\d•\-\*]+\.?\s+', '', text, flags=re.MULTILINE)
        text = text.encode('ascii', 'ignore').decode('ascii')
        text = " ".join(text.split())
        return text.strip()

    async def say(self, text: str):
        async def string_to_generator(t):
            yield t
        await self.say_stream(string_to_generator(text))

    async def say_stream(self, token_generator):
        """
        Ordered Streaming: Downloads in parallel but plays in strict sequence.
        """
        self._is_interrupted = False
        queue = asyncio.Queue()
        player_task = asyncio.create_task(self._player(queue))
        
        sentence_buffer = ""
        chunk_count = 0
        first_sentence = True

        try:
            async for token in token_generator:
                if self._is_interrupted:
                    break
                
                sentence_buffer += token
                current_limit = 20 if first_sentence else 80

                if any(p in token for p in ".!?\n") and len(sentence_buffer) > current_limit:
                    clean_text = self._clean_text_for_speech(sentence_buffer)
                    
                    if len(clean_text) > 2 and any(c.isalpha() for c in clean_text):
                        file_path = os.path.join(self.temp_dir, f"chunk_{chunk_count}.mp3")
                        
                        # WE QUEUE THE DOWNLOAD TASK ITSELF
                        # This ensures the player consumes them in the correct index order
                        download_task = asyncio.create_task(self._download_file(clean_text, file_path))
                        await queue.put((download_task, file_path))
                        
                        chunk_count += 1
                        first_sentence = False
                    
                    sentence_buffer = ""

            # Handle leftovers
            if sentence_buffer.strip() and not self._is_interrupted:
                clean_text = self._clean_text_for_speech(sentence_buffer)
                if len(clean_text) > 2:
                    file_path = os.path.join(self.temp_dir, f"last_chunk.mp3")
                    download_task = asyncio.create_task(self._download_file(clean_text, file_path))
                    await queue.put((download_task, file_path))

        finally:
            await queue.put((None, None)) # Signal player to stop
            await player_task

    async def _download_file(self, text, path):
        """Pure download logic."""
        with open(path, "wb") as f:
            async for chunk in self.provider.generate_stream(text):
                f.write(chunk)
        return path

    async def _player(self, queue):
        """The Consumer: Awaits the specific task in the queue before playing."""
        while True:
            task, file_path = await queue.get()
            if task is None or self._is_interrupted:
                break

            try:
                # WAIT for the specific download to finish before playing
                await task 
                
                if os.path.exists(file_path):
                    self._current_process = await asyncio.create_subprocess_exec(
                        'afplay', file_path,
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    await self._current_process.wait()
            except Exception as e:
                pass
            finally:
                if file_path and os.path.exists(file_path):
                    try: os.remove(file_path)
                    except: pass
                queue.task_done()

    def stop(self):
        self._is_interrupted = True
        if self._current_process and self._current_process.returncode is None:
            try: self._current_process.terminate()
            except: pass
        subprocess.run(["killall", "afplay"], stderr=subprocess.DEVNULL)
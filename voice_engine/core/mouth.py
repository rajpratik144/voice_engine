# import subprocess
# import asyncio
# import os
# from ..providers.base import TTSProvider

# class Mouth:
#     """
#     The Mouth Module: Handles audio playback and hardware interaction.
#     Optimized for older MacBooks by using the native 'afplay' utility.
#     """
    
#     def __init__(self, provider: TTSProvider):
#         """
#         Dependency Injection: We 'inject' the TTS provider (e.g., EdgeTTS).
#         """
#         self.provider = provider
#         self.temp_file = "temp_speech.mp3"
#         self._current_process = None

#     async def say(self, text: str):
#         """
#         Converts text to speech and plays it using the macOS native player.
#         """
#         print(f"AI: {text}")

#         try:
#             # 1. Download and Buffer the audio
#             # We save to a file because 'afplay' is more stable with files 
#             # than with pipes on older Intel hardware.
#             with open(self.temp_file, "wb") as f:
#                 async for chunk in self.provider.generate_stream(text):
#                     f.write(chunk)

#             # 2. Execute native 'afplay'
#             # This uses the macOS CoreAudio framework (extremely lightweight)
#             self._current_process = await asyncio.create_subprocess_exec(
#                 'afplay', self.temp_file,
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.DEVNULL
#             )

#             # Wait for the AI to finish speaking
#             await self._current_process.wait()

#         except Exception as e:
#             print(f"Error during playback: {e}")
        
#         finally:
#             # 3. Clean up
#             self._cleanup()

#     def _cleanup(self):
#         """Removes the temporary audio file from the SSD."""
#         if os.path.exists(self.temp_file):
#             try:
#                 os.remove(self.temp_file)
#             except PermissionError:
#                 pass # File might still be locked by the OS
#         self._current_process = None

#     def stop(self):
#         """
#         Barge-in: Immediately stops the audio playback by killing
#         the 'afplay' process.
#         """
#         if self._current_process and self._current_process.returncode is None:
#             try:
#                 self._current_process.terminate()
#                 print("Playback Interrupted (Barge-In).")
#             except Exception:
#                 # If terminate fails, we force kill the system player
#                 subprocess.run(["killall", "afplay"], stderr=subprocess.DEVNULL)

# import pygame
# import io
# import asyncio
# from ..providers.base import TTSProvider

# class Mouth:
#     def __init__(self, provider: TTSProvider):
#         self.provider = provider
#         # Initialize the audio mixer
#         pygame.mixer.init(frequency=24000) 

#     async def say(self, text: str):
#         """
#         Plays speech with reduced latency by using an in-memory buffer.
#         """
#         print(f"AI: {text}")
        
#         # 1. Collect audio chunks into an In-Memory Bytes Buffer
#         # This is much faster than writing to the SSD
#         audio_data = bytearray()
        
#         async for chunk in self.provider.generate_stream(text):
#             audio_data.extend(chunk)
            
#             # Optimization: Start playing once we have enough data (e.g., 32kb)
#             # but for now, we'll load the full buffer to keep it simple and stable
        
#         # 2. Play from RAM
#         audio_stream = io.BytesIO(audio_data)
#         pygame.mixer.music.load(audio_stream)
#         pygame.mixer.music.play()

#         # 3. Wait for it to finish
#         while pygame.mixer.music.get_busy():
#             await asyncio.sleep(0.1)

#     def stop(self):
#         """Immediate stop for Barge-in."""
#         pygame.mixer.music.stop()


# import subprocess
# import asyncio
# import os
# import re
# from ..providers.base import TTSProvider

# class Mouth:
#     def __init__(self, provider: TTSProvider):
#         self.provider = provider
#         self.temp_dir = "temp_audio"
#         self._current_process = None
#         self._is_interrupted = False
        
#         # Create a temp directory to store sentence chunks
#         if not os.path.exists(self.temp_dir):
#             os.makedirs(self.temp_dir)

#     def _split_text(self, text: str):
#         """Splits text into sentences based on punctuation."""
#         # This ensures we don't wait for a whole paragraph
#         sentences = re.split(r'(?<=[.!?]) +', text)
#         return [s for s in sentences if s.strip()]

#     async def _play_chunk(self, file_path: str):
#         """Plays a single audio file and waits for it to finish."""
#         if self._is_interrupted:
#             return

#         self._current_process = await asyncio.create_subprocess_exec(
#             'afplay', file_path,
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.DEVNULL
#         )
#         await self._current_process.wait()

#     async def say(self, text: str):
#         """
#         Plays speech sentence-by-sentence to keep latency low.
#         """
#         self._is_interrupted = False
#         sentences = self._split_text(text)
        
#         # We will use two tasks: one for downloading, one for playing
#         for i, sentence in enumerate(sentences):
#             if self._is_interrupted:
#                 break
                
#             chunk_file = os.path.join(self.temp_dir, f"chunk_{i}.mp3")
            
#             # 1. Download the current sentence
#             # (In a more advanced version, we'd pre-download chunk i+1)
#             with open(chunk_file, "wb") as f:
#                 async for chunk in self.provider.generate_stream(sentence):
#                     f.write(chunk)
            
#             # 2. Play the sentence chunk
#             await self._play_chunk(chunk_file)
            
#             # 3. Clean up the chunk
#             if os.path.exists(chunk_file):
#                 os.remove(chunk_file)

#     def stop(self):
#         """Immediate Barge-in."""
#         self._is_interrupted = True
#         if self._current_process and self._current_process.returncode is None:
#             self._current_process.terminate()
#         # Kill any remaining afplay processes
#         subprocess.run(["killall", "afplay"], stderr=subprocess.DEVNULL)


# import subprocess
# import asyncio
# import os
# import re
# from ..providers.base import TTSProvider

# class Mouth:
#     def __init__(self, provider: TTSProvider):
#         self.provider = provider
#         self.temp_dir = "temp_audio"
#         self._current_process = None
#         self._is_interrupted = False
        
#         if not os.path.exists(self.temp_dir):
#             os.makedirs(self.temp_dir)

#     def _split_text(self, text: str):
#         """Splits text into sentences."""
#         sentences = re.split(r'(?<=[.!?]) +', text)
#         return [s for s in sentences if s.strip()]

#     async def _downloader(self, sentences, queue):
#         """Background task: Downloads sentences into the queue as fast as possible."""
#         for i, sentence in enumerate(sentences):
#             if self._is_interrupted:
#                 break
            
#             file_path = os.path.join(self.temp_dir, f"chunk_{i}.mp3")
            
#             # Download the chunk
#             with open(file_path, "wb") as f:
#                 async for chunk in self.provider.generate_stream(sentence):
#                     f.write(chunk)
            
#             # Put the file path in the queue for the player to find
#             await queue.put(file_path)
        
#         # Signal the player that we are done downloading
#         await queue.put(None)

#     async def _player(self, queue):
#         """Foreground task: Plays files from the queue immediately."""
#         while True:
#             file_path = await queue.get()
            
#             # If we get None, the downloader is finished
#             if file_path is None or self._is_interrupted:
#                 break

#             # Use afplay to play the file
#             self._current_process = await asyncio.create_subprocess_exec(
#                 'afplay', file_path,
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.DEVNULL
#             )
#             await self._current_process.wait()
            
#             # Clean up the file after playing
#             if os.path.exists(file_path):
#                 os.remove(file_path)
            
#             queue.task_done()

#     async def say(self, text: str):
#         """
#         The Orchestrator: Runs downloader and player at the same time.
#         """
#         self._is_interrupted = False
#         sentences = self._split_text(text)
#         queue = asyncio.Queue()

#         # Start both tasks simultaneously
#         # gather() lets them run in parallel
#         await asyncio.gather(
#             self._downloader(sentences, queue),
#             self._player(queue)
#         )

#     def stop(self):
#         """Barge-in: Kills the current process and flags the loop to stop."""
#         self._is_interrupted = True
#         if self._current_process and self._current_process.returncode is None:
#             self._current_process.terminate()
#         subprocess.run(["killall", "afplay"], stderr=subprocess.DEVNULL)

# import subprocess
# import asyncio
# import os
# import re
# from ..providers.base import TTSProvider

# class Mouth:
#     def __init__(self, provider: TTSProvider):
#         self.provider = provider
#         self.temp_dir = "temp_audio"
#         self._current_process = None
#         self._is_interrupted = False
        
#         if not os.path.exists(self.temp_dir):
#             os.makedirs(self.temp_dir)

#     async def say_stream(self, token_generator):
#         """
#         Consumes tokens from an LLM and speaks sentences as they are completed.
#         This is the fastest way to handle long AI responses.
#         """
#         self._is_interrupted = False
#         queue = asyncio.Queue()
        
#         # Start the player in the background
#         player_task = asyncio.create_task(self._player(queue))
        
#         sentence_buffer = ""
#         chunk_count = 0

#         async for token in token_generator:
#             if self._is_interrupted:
#                 break
                
#             sentence_buffer += token
            
#             # Check if the buffer now contains a full sentence
#             if any(punct in token for punct in ".!?\n"):
#                 clean_sentence = sentence_buffer.strip()
#                 if clean_sentence:
#                     # Download and queue this sentence IMMEDIATELY
#                     file_path = os.path.join(self.temp_dir, f"stream_chunk_{chunk_count}.mp3")
#                     await self._download_and_queue(clean_sentence, file_path, queue)
#                     chunk_count += 1
#                     sentence_buffer = "" # Reset for next sentence

#         # Handle any leftover text in the buffer
#         if sentence_buffer.strip() and not self._is_interrupted:
#             file_path = os.path.join(self.temp_dir, f"stream_chunk_{chunk_count}.mp3")
#             await self._download_and_queue(sentence_buffer.strip(), file_path, queue)

#         # Signal end of stream
#         await queue.put(None)
#         await player_task

#     async def _download_and_queue(self, text, file_path, queue):
#         """Helper to download a chunk and put it in the play queue."""
#         with open(file_path, "wb") as f:
#             async for chunk in self.provider.generate_stream(text):
#                 f.write(chunk)
#         await queue.put(file_path)

#     async def _player(self, queue):
#         """Plays files from the queue as soon as they arrive."""
#         while True:
#             file_path = await queue.get()
#             if file_path is None or self._is_interrupted:
#                 break

#             self._current_process = await asyncio.create_subprocess_exec(
#                 'afplay', file_path,
#                 stdout=subprocess.DEVNULL,
#                 stderr=subprocess.DEVNULL
#             )
#             await self._current_process.wait()
            
#             if os.path.exists(file_path):
#                 os.remove(file_path)
#             queue.task_done()

#     def stop(self):
#         """Immediate Barge-in."""
#         self._is_interrupted = True
#         if self._current_process and self._current_process.returncode is None:
#             self._current_process.terminate()
#         subprocess.run(["killall", "afplay"], stderr=subprocess.DEVNULL)

# import subprocess
# import asyncio
# import os
# import re
# from ..providers.base import TTSProvider

# class Mouth:
#     """
#     The Mouth Module: Handles streaming audio playback.
#     Optimized for low-latency on 2015 MacBook Air.
#     """
#     def __init__(self, provider: TTSProvider):
#         self.provider = provider
#         self.temp_dir = "temp_audio"
#         self._current_process = None
#         self._is_interrupted = False
        
#         # Ensure temp directory exists
#         if not os.path.exists(self.temp_dir):
#             os.makedirs(self.temp_dir, exist_ok=True)

#     async def say(self, text: str):
#         """
#         Simple method to speak a static string.
#         """
#         async def string_to_generator(t):
#             yield t
        
#         await self.say_stream(string_to_generator(text))

#     async def say_stream(self, token_generator):
#         """
#         The Core Engine: Background downloads + Parallel playback.
#         """
#         self._is_interrupted = False
#         queue = asyncio.Queue()
        
#         # 1. Start the player in the background
#         player_task = asyncio.create_task(self._player(queue))
        
#         sentence_buffer = ""
#         chunk_count = 0

#         # 2. Process tokens from the Brain (RAG Engine)
#         async for token in token_generator:
#             if self._is_interrupted:
#                 break
                
#             sentence_buffer += token
            
#             # If we hit a sentence ender, trigger a background download
#             if any(punct in token for punct in ".!?\n"):
#                 clean_sentence = sentence_buffer.strip()
#                 if len(clean_sentence) > 1:
#                     file_path = os.path.join(self.temp_dir, f"chunk_{chunk_count}.mp3")
                    
#                     # Start download as a background task (Fast!)
#                     asyncio.create_task(self._download_and_enqueue(clean_sentence, file_path, queue))
                    
#                     chunk_count += 1
#                     sentence_buffer = ""

#         # 3. Handle leftover text
#         if sentence_buffer.strip() and not self._is_interrupted:
#             file_path = os.path.join(self.temp_dir, f"last_chunk.mp3")
#             asyncio.create_task(self._download_and_enqueue(sentence_buffer.strip(), file_path, queue))

#         # 4. Wait for downloads and player to finish
#         await asyncio.sleep(0.5) 
#         await queue.put(None) # Signal player to stop
#         await player_task

#     async def _download_and_enqueue(self, text, path, queue):
#         """Downloads audio and adds the file path to the playback queue."""
#         try:
#             with open(path, "wb") as f:
#                 async for chunk in self.provider.generate_stream(text):
#                     f.write(chunk)
#             await queue.put(path)
#         except Exception as e:
#             print(f"\n[TTS Error]: {e}")

#     async def _player(self, queue):
#         """
#         The Consumer: Plays files from the queue as soon as they are ready.
#         """
#         while True:
#             file_path = await queue.get()
            
#             # Exit if we get the signal or an interruption
#             if file_path is None or self._is_interrupted:
#                 break

#             try:
#                 # Use native afplay for zero-CPU strain
#                 self._current_process = await asyncio.create_subprocess_exec(
#                     'afplay', file_path,
#                     stdout=subprocess.DEVNULL,
#                     stderr=subprocess.DEVNULL
#                 )
#                 await self._current_process.wait()
#             finally:
#                 # Clean up file immediately after playing
#                 if os.path.exists(file_path):
#                     try:
#                         os.remove(file_path)
#                     except:
#                         pass
#                 queue.task_done()

#     def stop(self):
#         """
#         Barge-in: Kills current audio and stops future downloads.
#         """
#         self._is_interrupted = True
#         if self._current_process and self._current_process.returncode is None:
#             try:
#                 self._current_process.terminate()
#             except:
#                 pass
#         # Hard kill for safety
#         subprocess.run(["killall", "afplay"], stderr=subprocess.DEVNULL)

# import subprocess
# import asyncio
# import os
# import re
# from ..providers.base import TTSProvider

# class Mouth:
#     def __init__(self, provider: TTSProvider):
#         self.provider = provider
#         self.temp_dir = "temp_audio"
#         self._current_process = None
#         self._is_interrupted = False
        
#         if not os.path.exists(self.temp_dir):
#             os.makedirs(self.temp_dir, exist_ok=True)

#     def _clean_text_for_speech(self, text: str) -> str:
#         """
#         Removes Markdown and symbols that cause TTS errors.
#         """
#         # 1. Remove Bold/Italic (asterisks)
#         text = text.replace("**", "").replace("*", "")
        
#         # 2. Remove Markdown Table borders and horizontal lines
#         text = text.replace("|", " ").replace("---", "")
        
#         # 3. Remove excessive dashes or special symbols
#         text = re.sub(r'[-_]{2,}', '', text)
        
#         # 4. Clean up whitespace
#         text = " ".join(text.split())
        
#         return text.strip()

#     async def say(self, text: str):
#         async def string_to_generator(t):
#             yield t
#         await self.say_stream(string_to_generator(text))

#     async def say_stream(self, token_generator):
#         self._is_interrupted = False
#         queue = asyncio.Queue()
#         player_task = asyncio.create_task(self._player(queue))
        
#         sentence_buffer = ""
#         chunk_count = 0

#         async for token in token_generator:
#             if self._is_interrupted:
#                 break
                
#             sentence_buffer += token
            
#             # Split on sentence enders
#             if any(punct in token for punct in ".!?\n"):
#                 raw_sentence = sentence_buffer.strip()
#                 # CLEAN THE TEXT before sending to TTS
#                 clean_sentence = self._clean_text_for_speech(raw_sentence)
                
#                 # Only try to speak if there are actually words left
#                 if len(clean_sentence) > 1 and any(c.isalpha() for c in clean_sentence):
#                     file_path = os.path.join(self.temp_dir, f"chunk_{chunk_count}.mp3")
#                     asyncio.create_task(self._download_and_enqueue(clean_sentence, file_path, queue))
#                     chunk_count += 1
                
#                 sentence_buffer = ""

#         # Handle leftovers
#         if sentence_buffer.strip() and not self._is_interrupted:
#             clean_leftover = self._clean_text_for_speech(sentence_buffer)
#             if len(clean_leftover) > 1 and any(c.isalpha() for c in clean_leftover):
#                 file_path = os.path.join(self.temp_dir, f"last_chunk.mp3")
#                 asyncio.create_task(self._download_and_enqueue(clean_leftover, file_path, queue))

#         await asyncio.sleep(1) 
#         await queue.put(None) 
#         await player_task

#     async def _download_and_enqueue(self, text, path, queue):
#         try:
#             with open(path, "wb") as f:
#                 async for chunk in self.provider.generate_stream(text):
#                     f.write(chunk)
#             await queue.put(path)
#         except Exception as e:
#             # We fail silently here so the app keeps running if one chunk fails
#             pass 

#     async def _player(self, queue):
#         while True:
#             file_path = await queue.get()
#             if file_path is None or self._is_interrupted:
#                 break
#             try:
#                 self._current_process = await asyncio.create_subprocess_exec(
#                     'afplay', file_path,
#                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
#                 )
#                 await self._current_process.wait()
#             finally:
#                 if os.path.exists(file_path):
#                     os.remove(file_path)
#                 queue.task_done()

#     def stop(self):
#         self._is_interrupted = True
#         if self._current_process and self._current_process.returncode is None:
#             self._current_process.terminate()
#         subprocess.run(["killall", "afplay"], stderr=subprocess.DEVNULL)

# import subprocess
# import asyncio
# import os
# import re
# from ..providers.base import TTSProvider

# class Mouth:
#     def __init__(self, provider: TTSProvider):
#         self.provider = provider
#         self.temp_dir = "temp_audio"
#         self._current_process = None
#         self._is_interrupted = False
        
#         if not os.path.exists(self.temp_dir):
#             os.makedirs(self.temp_dir, exist_ok=True)

#     def _clean_text_for_speech(self, text: str) -> str:
#         text = re.sub(r'\|?[\s\-]*[\-:]{3,}[\s\- |]*', ' ', text)
#         text = text.replace("|", " ").replace("**", "").replace("*", "").replace("#", "")
#         text = re.sub(r'^\s*[\d•\-\*]+\.?\s+', '', text, flags=re.MULTILINE)
#         text = text.encode('ascii', 'ignore').decode('ascii')
#         text = " ".join(text.split())
#         return text.strip()

#     async def say(self, text: str):
#         async def string_to_generator(t):
#             yield t
#         await self.say_stream(string_to_generator(text))

#     async def say_stream(self, token_generator):
#         self._is_interrupted = False
#         queue = asyncio.Queue()
#         player_task = asyncio.create_task(self._player(queue))
        
#         # Track background downloads
#         download_tasks = []
        
#         sentence_buffer = ""
#         chunk_count = 0
#         first_sentence = True

#         async for token in token_generator:
#             if self._is_interrupted:
#                 break
            
#             # print(token, end="", flush=True) # Real-time text display
#             sentence_buffer += token
            
#             current_limit = 20 if first_sentence else 80

#             if any(p in token for p in ".!?\n") and len(sentence_buffer) > current_limit:
#                 clean_text = self._clean_text_for_speech(sentence_buffer)
                
#                 if len(clean_text) > 2 and any(c.isalpha() for c in clean_text):
#                     file_path = os.path.join(self.temp_dir, f"chunk_{chunk_count}.mp3")
                    
#                     # Create the task and track it
#                     task = asyncio.create_task(self._download_and_enqueue(clean_text, file_path, queue))
#                     download_tasks.append(task)
                    
#                     chunk_count += 1
#                     first_sentence = False
                
#                 sentence_buffer = ""

#         # Handle leftovers
#         if sentence_buffer.strip() and not self._is_interrupted:
#             clean_text = self._clean_text_for_speech(sentence_buffer)
#             if len(clean_text) > 2 and any(c.isalpha() for c in clean_text):
#                 file_path = os.path.join(self.temp_dir, f"last_chunk.mp3")
#                 task = asyncio.create_task(self._download_and_enqueue(clean_text, file_path, queue))
#                 download_tasks.append(task)

#         # CRITICAL FIX: Wait for all downloads to finish before signalling the player
#         if download_tasks:
#             await asyncio.gather(*download_tasks)

#         # Signal player to stop after all files are in the queue
#         await queue.put(None) 
#         await player_task

#     async def _download_and_enqueue(self, text, path, queue):
#         try:
#             # We use a short retry logic for Edge-TTS
#             for attempt in range(2):
#                 with open(path, "wb") as f:
#                     async for chunk in self.provider.generate_stream(text):
#                         f.write(chunk)
                
#                 if os.path.exists(path) and os.path.getsize(path) > 0:
#                     await queue.put(path)
#                     return # Success
#                 await asyncio.sleep(0.5)
#         except Exception as e:
#             print(f"\n[Mouth] Download error: {e}")

#     async def _player(self, queue):
#         while True:
#             file_path = await queue.get()
#             if file_path is None or self._is_interrupted:
#                 break

#             try:
#                 self._current_process = await asyncio.create_subprocess_exec(
#                     'afplay', file_path,
#                     stdout=subprocess.DEVNULL,
#                     stderr=subprocess.DEVNULL
#                 )
#                 await self._current_process.wait()
#             except Exception as e:
#                 print(f"\n[Mouth] Playback error: {e}")
#             finally:
#                 if os.path.exists(file_path):
#                     try: os.remove(file_path)
#                     except: pass
#                 queue.task_done()

#     def stop(self):
#         self._is_interrupted = True
#         if self._current_process and self._current_process.returncode is None:
#             try: self._current_process.terminate()
#             except: pass
#         subprocess.run(["killall", "afplay"], stderr=subprocess.DEVNULL)

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
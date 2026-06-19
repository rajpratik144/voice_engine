# import asyncio
# from voice_engine.providers.tts_edge import EdgeTTSProvider
# from voice_engine.core.mouth import Mouth

# async def main():
#     # 1. Dependency Injection (Injecting the free provider into the Mouth)
#     # We use a high-quality Neural voice
#     provider = EdgeTTSProvider(voice="en-US-AndrewNeural")
#     mouth = Mouth(provider=provider)

#     # 2. Execution
#     # Since we are using asyncio, this won't freeze your Mac
#     print("--- Starting Voice Engine Test ---")
#     await mouth.say("The morning sun rose slowly over the hills, casting a warm golden light across the valley. Birds moved through the trees while a gentle breeze carried the scent of fresh grass and wildflowers. In the distance, a small river reflected the colors of the sky, creating a peaceful scene that seemed untouched by time. People often underestimate the importance of quiet moments like these, yet they provide an opportunity to pause, reflect, and appreciate the world around us. Whether someone is beginning a new journey, working toward an ambitious goal, or simply enjoying a calm day, nature has a unique way of reminding us that progress happens step by step. Every challenge teaches a lesson, every success builds confidence, and every experience contributes to personal growth. By remaining curious, patient, and consistent, anyone can develop new skills, overcome obstacles, and create opportunities that once seemed impossible. The future is shaped not only by grand achievements but also by the small actions taken every day, and those actions, repeated over time, often lead to extraordinary results.")    
#     print("--- Test Complete ---")

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         # If you press Ctrl+C, the voice stops immediately
#         print("\nStopping...")

# *********************************************************************************************************
# *********************************************************************************************************
# import asyncio
# import os
# from dotenv import load_dotenv

# # Import our Modular Voice Engine
# from voice_engine.providers.stt_groq import GroqSTTProvider
# from voice_engine.providers.tts_edge import EdgeTTSProvider
# from voice_engine.core.ear import Ear
# from voice_engine.core.mouth import Mouth

# # 1. Load your API Key from the .env file
# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# async def main():
#     # 2. Check for API Key
#     if not GROQ_API_KEY:
#         print("ERROR: Please add your GROQ_API_KEY to the .env file.")
#         return

#     # 3. Initialization (Dependency Injection)
#     # The Ear setup
#     stt_provider = GroqSTTProvider(api_key=GROQ_API_KEY)
#     ear = Ear(provider=stt_provider, silence_threshold=1000)

#     # The Mouth setup
#     tts_provider = EdgeTTSProvider(voice="en-US-AndrewNeural")
#     mouth = Mouth(provider=tts_provider)

#     print("--- Modular Voice Engine Initialized ---")
#     await mouth.say("Hello Pratik. I am listening. Tell me something, and I will repeat it back to you.")

#     try:
#         while True:
#             # A. The Ear listens
#             # This blocks until silence is detected
#             user_text = await ear.listen()
            
#             if not user_text or user_text.strip() == "":
#                 print("System: I didn't hear anything.")
#                 continue

#             print(f"You said: {user_text}")

#             # B. Check for exit command
#             if "goodbye" in user_text.lower() or "exit" in user_text.lower():
#                 await mouth.say("Goodbye! Powering down.")
#                 break

#             # C. The Mouth responds (The Echo)
#             response = f"You just said: {user_text}"
#             await mouth.say(response)

#     except KeyboardInterrupt:
#         print("\nStopping the engine...")
#     finally:
#         print("Engine shut down.")

# if __name__ == "__main__":
#     asyncio.run(main())

# import asyncio
# import os
# from dotenv import load_dotenv
# from voice_engine.providers.stt_groq import GroqSTTProvider
# from voice_engine.providers.tts_edge import EdgeTTSProvider
# from voice_engine.core.ear import Ear
# from voice_engine.core.mouth import Mouth

# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# async def monitor_interruption(ear, mouth):
#     """
#     This task runs in the background. If it hears a loud noise
#     while the mouth is busy, it tells the mouth to shut up.
#     """
#     while True:
#         # We only check for interruption if the AI is actually speaking
#         # (In our case, we check if afplay is running)
#         if mouth._current_process and mouth._current_process.returncode is None:
#             if ear.is_someone_talking():
#                 print("\n[Barge-in Detected!]")
#                 mouth.stop()
#                 break # Stop monitoring once we've interrupted
#         await asyncio.sleep(0.1) # Small sleep to save 2015 CPU

# async def speak_with_bargein(text, mouth, ear):
#     """
#     A wrapper that speaks while a monitor listens for interruptions.
#     """
#     # Start the background monitor
#     monitor_task = asyncio.create_task(monitor_interruption(ear, mouth))
    
#     # Start the AI speaking
#     await mouth.say(text)
    
#     # Once speech is done (or stopped), cancel the monitor
#     monitor_task.cancel()

# async def main():
#     stt_provider = GroqSTTProvider(api_key=GROQ_API_KEY)
#     ear = Ear(provider=stt_provider, silence_threshold=1200) # Increased threshold slightly

#     tts_provider = EdgeTTSProvider(voice="en-US-AndrewNeural")
#     mouth = Mouth(provider=tts_provider)

#     print("--- System Ready: Speak naturally ---")
    
#     try:
#         while True:
#             # 1. Listen for user input
#             user_text = await ear.listen()
#             if not user_text: continue
            
#             print(f"You: {user_text}")

#             if "goodbye" in user_text.lower() or "exit" in user_text.lower():
#                 await mouth.say("Goodbye! Powering down.")
#                 break

#             # 2. Respond with Barge-in capability
#             response = f"you just said: {user_text}. You can interrupt me anytime."
#             await speak_with_bargein(response, mouth, ear)

#     except KeyboardInterrupt:
#         print("Shutting down...")

# if __name__ == "__main__":
#     asyncio.run(main())



# ==========================================
# File: main.py
# ==========================================


import asyncio
import os
from dotenv import load_dotenv
from voice_engine.providers.tts_edge import EdgeTTSProvider
from voice_engine.core.mouth import Mouth

async def mock_llm_generator():
    """Simulates an LLM (like Gemini) yielding tokens one by one."""
    text = "The morning sun rose slowly over the hills, casting a warm golden light across the valley. Birds moved through the trees while a gentle breeze carried the scent of fresh grass and wildflowers. In the distance, a small river reflected the colors of the sky, creating a peaceful scene that seemed untouched by time. People often underestimate the importance of quiet moments like these, yet they provide an opportunity to pause, reflect, and appreciate the world around us. Whether someone is beginning a new journey, working toward an ambitious goal, or simply enjoying a calm day, nature has a unique way of reminding us that progress happens step by step. Every challenge teaches a lesson, every success builds confidence, and every experience contributes to personal growth. By remaining curious, patient, and consistent, anyone can develop new skills, overcome obstacles, and create opportunities that once seemed impossible. The future is shaped not only by grand achievements but also by the small actions taken every day, and those actions, repeated over time, often lead to extraordinary results."
    tokens = text.split(" ")
    for token in tokens:
        yield token + " "
        await asyncio.sleep(0.2) # Simulate thinking/generation delay

async def main():
    tts_provider = EdgeTTSProvider()
    mouth = Mouth(provider=tts_provider)

    print("--- Testing Streaming Output ---")
    print("AI is starting to 'think'...")
    
    # We pass the GENERATOR directly to the mouth
    # The AI will start talking before the generator is even finished!
    await mouth.say_stream(mock_llm_generator())

    print("--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
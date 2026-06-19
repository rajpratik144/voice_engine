
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
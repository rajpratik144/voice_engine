import asyncio
import os
from dotenv import load_dotenv

# Import Module 2 (Voice)
from voice_engine.core.ear import Ear
from voice_engine.core.mouth import Mouth
from voice_engine.core.assistant import VoiceAssistant
from voice_engine.providers.stt_groq import GroqSTTProvider
from voice_engine.providers.tts_edge import EdgeTTSProvider

# Import Module 1 (RAG - Assuming your rag_engine structure)
# from rag_engine.core import RAGSystem 

load_dotenv()

# --- MOCK RAG ENGINE (Replace this with your Module 1 code) ---
async def mock_rag_engine(query):
    """
    This simulates your Llama 3 / Gemini RAG system.
    In your real code, this will search Pinecone/Supabase.
    """
    # Simulate a thinking delay
    await asyncio.sleep(1) 
    
    response = f"I have searched your documents for information about {query}. Based on the context, here is what I found. It is very interesting!"
    for word in response.split():
        yield word + " "
        await asyncio.sleep(0.1) # Simulate token generation speed

# --- MAIN EXECUTION ---
async def main():
    # 1. Setup Voice Providers
    stt = GroqSTTProvider(api_key=os.getenv("GROQ_API_KEY"))
    tts = EdgeTTSProvider()
    
    # 2. Setup Core Modules
    ear = Ear(provider=stt, silence_threshold=1200)
    mouth = Mouth(provider=tts)
    
    # 3. Setup Orchestrator
    assistant = VoiceAssistant(ear, mouth)

    print("--- ASSISTANT ONLINE ---")
    await assistant.say("Assistant online. How can I help you with your documents today?")

    # 4. Run the Full-Duplex Loop
    # We pass our RAG engine (mock_rag_engine) as the callback
    await assistant.listen_and_process(brain_callback=mock_rag_engine)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSystem offline.")
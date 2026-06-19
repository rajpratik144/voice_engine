import asyncio
from .ear import Ear
from .mouth import Mouth

class VoiceAssistant:
    """
    The Orchestrator: Combines Ear and Mouth into a single high-level interface.
    This is what the Parent System (RAG) interacts with.
    """
    def __init__(self, ear: Ear, mouth: Mouth):
        self.ear = ear
        self.mouth = mouth

    async def listen_and_process(self, brain_callback):
        """
        1. Listens for user voice.
        2. Sends text to the 'brain_callback' (Your RAG Engine).
        3. Streams the response through the Mouth.
        """
        while True:
            # A. Wait for user to speak
            user_text = await self.ear.listen()
            
            if not user_text or len(user_text.strip()) < 2:
                continue
                
            print(f"User: {user_text}")

            # B. Check for interruption (Barge-in) monitoring
            # We wrap the RAG call and the Mouth call in a way that
            # allows the Ear to kill the Mouth if the user speaks.
            
            # C. Call the RAG Engine (The Brain)
            # We assume the brain_callback returns an ASYNC GENERATOR of tokens
            response_generator = brain_callback(user_text)
            
            # D. Speak the response
            # Note: say_stream handles the sentence buffering internally
            await self.mouth.say_stream(response_generator)

    async def say(self, text: str):
        """Public method to make the assistant speak a simple string."""
        await self.mouth.say(text)
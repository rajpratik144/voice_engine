
---

### **GitHub Repository Metadata**

**Description:**
A modular, provider-agnostic, and stateless Voice Intelligence library featuring real-time STT/TTS streaming, parallel processing, and intelligent barge-in detection. Optimized for high-performance interaction on low-resource hardware.

**Tags (Topics):**
`python` `voice-ai` `stt` `tts` `whisper` `groq` `edge-tts` `asyncio` `modular-architecture` `rag` `voice-assistant` `streaming-audio` `barge-in` `speech-to-text` `text-to-speech`

---

### **README.md**

```markdown
# Voice Intelligence Engine (Module 2)
**Creator: [Pratik Raj](https://github.com/yourusername)**

The Voice Intelligence (VI) Engine is a high-performance, stateless, and provider-agnostic Python library designed to act as the "Ear" and "Mouth" for AI systems. Built with a modular architecture, it allows for seamless integration with RAG engines, LLM services, or any logic layer via Dependency Injection.

Specifically optimized for low-latency streaming and efficiency on legacy hardware (e.g., Intel-based MacBooks), this engine ensures natural, human-like conversation flow.

---

## 🚀 Core Features

- **The Ear (STT):** High-speed transcription using Groq (Whisper-Large-V3) with local Voice Activity Detection (VAD).
- **The Mouth (TTS):** Neural voice synthesis via Edge-TTS, featuring parallel sentence streaming for near-zero "Dead Air" latency.
- **Intelligent Barge-in:** Real-time interruption detection. The system monitors microphone levels while speaking and kills audio playback the moment user speech is detected.
- **Provider-Agnostic:** Built using Abstract Base Classes; swap your STT/TTS providers (e.g., ElevenLabs, OpenAI, Deepgram) without touching core logic.
- **Markdown-Safe:** Automated speech sanitization that converts Markdown tables and symbols into natural-sounding speech.

---

## 🛠 Hardware Prerequisites

To ensure low-latency audio playback without CPU strain, this system utilizes the macOS native `afplay` utility.

1. **System Drivers:** Ensure `portaudio` is installed.
   ```bash
   brew install portaudio
   ```
2. **Microphone Access:** Ensure your terminal/IDE has permissions to access the Microphone in *System Preferences > Security & Privacy*.

---

## 📦 Installation

Install the library directly from GitHub into your virtual environment by adding it in the requirements.txt file:

```bash
voice_engine @ git+https://github.com/rajpratik144/voice_engine.git
```

---

## ⚙️ Configuration

The system is configured via a dictionary passed to the `Ear` module. This allows you to calibrate the engine for different environments without modifying source code.

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `silence_threshold` | int | The volume level (RMS) required to trigger recording (Default: 1200). |
| `silence_duration` | float | Seconds of silence required before the Ear stops recording (Default: 1.5). |
| `sample_rate` | int | Audio frequency in Hz (Default: 16000 for Whisper). |

---

## 💻 Standalone Usage Example

This example demonstrates a basic "Echo" assistant using the library.

```python
import asyncio
import os
from dotenv import load_dotenv
from voice_engine.core.ear import Ear
from voice_engine.core.mouth import Mouth
from voice_engine.providers.stt_groq import GroqSTTProvider
from voice_engine.providers.tts_edge import EdgeTTSProvider

load_dotenv()

async def main():
    # 1. Initialize Providers (Dependency Injection)
    stt_provider = GroqSTTProvider(api_key=os.getenv("GROQ_API_KEY"))
    tts_provider = EdgeTTSProvider(voice="en-US-AndrewNeural")

    # 2. Setup Modules with Config
    config = {"silence_threshold": 1200, "silence_duration": 1.2}
    ear = Ear(provider=stt_provider, config=config)
    mouth = Mouth(provider=tts_provider)

    print("--- System Ready ---")
    await mouth.say("Hello! I am your modular voice engine. Speak to me.")

    try:
        while True:
            # Ear listens for voice
            user_input = await ear.listen()
            if not user_input: continue
            
            print(f"User: {user_input}")

            # Mouth speaks response (supporting strings or generators)
            await mouth.say(f"You said: {user_input}")

            if "exit" in user_input.lower():
                break
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🧠 Integration with RAG Systems

The VI Engine is designed to be a "Peer" to intelligence layers. In a production RAG environment, you simply pass your LLM's **Async Token Generator** to the `mouth.say_stream()` method.

**Conceptual Workflow:**
1. `user_text = await ear.listen()`
2. `token_stream = rag_engine.ask_stream(user_text)`
3. `await mouth.say_stream(token_stream)`

This ensures the user hears the first sentence while the LLM is still generating the rest of the paragraph.

---

## 🏗 Architecture Details

- **Statelessness:** The library stores no conversation history, ensuring lightweight deployment and privacy.
- **Parallel Processing:** TTS synthesis and Audio playback run in parallel tasks.
- **Hardware Abstraction:** All audio playback is isolated to system-level subprocesses to prevent Python's Global Interpreter Lock (GIL) from causing audio stutters.

---

## 📄 License
MIT License. Created and maintained by **Pratik Raj**.


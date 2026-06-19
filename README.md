# Voice Intelligence Engine (Module 2)

A modular, provider-agnostic, and stateless Voice Intelligence library designed for low-latency human-AI interaction.

## Features
- **Ear (STT):** High-speed transcription via Groq (Whisper-Large-V3).
- **Mouth (TTS):** Neural voice synthesis via Edge-TTS with parallel sentence streaming.
- **Barge-in:** Real-time interruption handling using dynamic thresholding.
- **Hardware Optimized:** Designed to run efficiently on legacy hardware (Intel i5 / 8GB RAM).

## Architecture
This module follows a Dependency Injection pattern, allowing developers to swap STT/TTS providers without changing core logic.

## Installation
```bash
pip install -e .
```

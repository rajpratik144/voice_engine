# ==========================================
# File: setup.py
# ==========================================


from setuptools import setup, find_packages

setup(
    name="voice_engine",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "edge-tts",
        "groq",
        "aiohttp",
        "python-dotenv",
        "pyaudio"
    ],
)
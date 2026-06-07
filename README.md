## 🎬 Smart AI Video Translator & Dubber

A production-ready, highly efficient AI video translation and localized dubbing application built with **Streamlit**, **OpenAI's Whisper**, **Deep Translator**, and **Microsoft Edge TTS**. 

This application is designed with a **$0 operational cost architecture**, running entirely on free, open-source, and public endpoints. It features an integrated local license-key paywall system (`keys.txt`), allowing developers to easily monetize the tool using cryptocurrency or manual payment workflows.

---

## ✨ Key Features

* **🎙️ Localized Timeline Calibration:** Automatically parses audio into precise timestamped segments using Whisper to ensure translations match the original speaker's timing perfectly.
* **⚡ Dynamic Pacing Control:** Calculates the exact duration difference between the source text and translation, automatically adjusting the output speech rate to fit the original scene boundaries.
* **🔊 Free Neural Voices:** Utilizes high-quality, realistic neural text-to-speech voices across 10 global languages via Edge TTS.
* **🔑 Built-in SaaS Paywall:** Restricts access behind a secure lock screen until a valid license key mapping from `keys.txt` is provided.
* **🛡️ Zero API Costs:** No expensive OpenAI, ElevenLabs, or Google Cloud API subscriptions required. 100% pure profit margin.

---

## 🚀 Quick Setup & Local Deployment

### 1. Clone the Repository
```bash
git clone https://github.com/MZ-T3CH/ai-video-dubb.git

Navigate into the project directory:
cd ai-video-dubb

Install the required software packages:
Bash
pip install -r requirements.txt

Start the local interface panel:
streamlit run ai-dub-vid.py


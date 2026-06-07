import os
import tempfile
import asyncio
import streamlit as st
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import CompositeAudioClip
import whisper
from deep_translator import GoogleTranslator
import edge_tts

# =================================================
# LOCAL KEYS.TXT GATE SYSTEM
# =================================================

# Initialize authentication state if it doesn't exist yet
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_license_key(user_key):
    """Checks if the entered key exists inside keys.txt"""
    if not os.path.exists("keys.txt"):
        return False
    
    with open("keys.txt", "r") as f:
        # Read keys and strip out any hidden spaces, empty lines, or newlines
        valid_keys = [line.strip() for line in f.readlines() if line.strip()]
        
    return user_key.strip() in valid_keys

# Paywall / Lock Screen
if not st.session_state["authenticated"]:
    st.title("🔑 AI Video Translator - Premium Access")
    st.write("Welcome! This tool requires a valid premium license key to operate.")
    
    input_key = st.text_input("Enter your License Key:", type="password")
    
    if st.button("Verify & Unlock"):
        if check_license_key(input_key):
            st.session_state["authenticated"] = True
            st.success("Access Granted! Loading translator environment...")
            st.rerun()
        else:
            st.error("Invalid or expired license key. Please verify your access.")
            
    st.markdown("---")
    st.write("🪙 **How to Buy Access Using Cryptocurrency:**")
    st.info(
        "To get instant lifetime access, send **$10 (USDT / BTC)** to our wallet address below. "
        "Once transferred, contact support with your transaction confirmation proof to receive your unique license key!"
    )
    
    # Showcase your crypto wallet addresses cleanly here
    st.code("BTC: bc1qsgl3s5s77pckgkzj4xqncyp2jt7lklpxg0na42", language="text")
    st.code("Tron (TRC20): TNWJUi9reiCQnH36eiWeXVWLfF4EY2nKtA", language="text")
    
    st.stop() # Stops execution so unauthenticated users see nothing below

# =================================================
# SUPPORTED TRANSLATION DATA
# =================================================
EDGE_VOICES = {
    "English": {"Female (Ava)": "en-US-AvaNeural", "Male (Andrew)": "en-US-AndrewNeural"},
    "Urdu": {"Female (Uzma)": "ur-PK-UzmaNeural", "Male (Asad)": "ur-PK-AsadNeural"},
    "Hindi": {"Female (Swara)": "hi-IN-SwaraNeural", "Male (Madhur)": "hi-IN-MadhurNeural"},
    "Arabic": {"Female (Amina)": "ar-DZ-AminaNeural", "Male (Ali)": "ar-BH-AliNeural"},
    "French": {"Female (Denise)": "fr-FR-DeniseNeural", "Male (Henri)": "fr-FR-HenriNeural"},
    "Spanish": {"Female (Elvira)": "es-ES-ElviraNeural", "Male (Alvaro)": "es-ES-AlvaroNeural"},
    "German": {"Female (Amala)": "de-DE-AmalaNeural", "Male (Killian)": "de-DE-KillianNeural"},
    "Japanese": {"Female (Nanami)": "ja-JP-NanamiNeural", "Male (Keita)": "ja-JP-KeitaNeural"},
    "Russian": {"Female (Svetlana)": "ru-RU-SvetlanaNeural", "Male (Dmitry)": "ru-RU-DmitryNeural"},
    "Chinese": {"Female (Xiaoxiao)": "zh-CN-XiaoxiaoNeural", "Male (Yunxi)": "zh-CN-YunxiNeural"}
}

LANG_CODES = {
    "English": "en", "Urdu": "ur", "Hindi": "hi", "Arabic": "ar", "French": "fr",
    "Spanish": "es", "German": "de", "Japanese": "ja", "Russian": "ru", "Chinese": "zh-cn"
}

st.title("🎬 Smart AI Video Translator & Dubber by MZ")
st.write("Status: Premium Version Active ✅")

# =================================================
# SIDEBAR CONFIGURATION
# =================================================
st.sidebar.header("🎙️ Configuration")
model_size = st.sidebar.selectbox("Whisper Model Size", ["tiny", "base", "small", "medium"], index=1)
selected_language = st.sidebar.selectbox("Select Target Language", list(EDGE_VOICES.keys()))

available_voices = EDGE_VOICES[selected_language]
selected_voice_label = st.sidebar.selectbox("Select Dubbing Voice", list(available_voices.keys()))
voice_code = available_voices[selected_voice_label]

async def generate_edge_audio(text, voice, output_path, rate="+0%"):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)

# =================================================
# MAIN APPLICATION PIPELINE
# =================================================
uploaded_video = st.file_uploader("Upload Video", type=["mp4", "mkv", "avi", "mov"])

if st.button("Start Precision Video Dubbing"):
    if uploaded_video is None:
        st.error("Please upload a video.")
        st.stop()

    with st.spinner("Processing video segments and aligning timestamps..."):
        temp_files_to_clean = []
        audio_clips_to_close = []

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video.write(uploaded_video.read())
                video_path = temp_video.name
            temp_files_to_clean.append(video_path)

            temp_audio_path = "temp_extracted_audio.mp3"
            final_video_path = "translated_output_video.mp4"
            temp_files_to_clean.append(temp_audio_path)

            video = VideoFileClip(video_path)
            video.audio.write_audiofile(temp_audio_path, logger=None)

            st.info("Analyzing timeline timestamps via Whisper...")
            model = whisper.load_model(model_size)
            result = model.transcribe(temp_audio_path, task="transcribe")
            segments = result.get("segments", [])

            if not segments:
                st.warning("Could not map or identify any vocal text segments.")
                st.stop()

            lang_code = LANG_CODES[selected_language]
            translated_audio_clips = []

            st.info(f"Processing {len(segments)} timeline segments...")
            
            for idx, seg in enumerate(segments):
                if seg.get("text") is None:
                    continue
                orig_text = seg["text"].strip()
                if not orig_text or orig_text == "":
                    continue

                start_time = seg["start"]
                end_time = seg["end"]
                original_duration = end_time - start_time

                if original_duration <= 0:
                    continue

                trans_text = GoogleTranslator(source="auto", target=lang_code).translate(orig_text)
                if not trans_text or not trans_text.strip():
                    continue

                draft_seg_path = f"draft_seg_{idx}.mp3"
                final_seg_path = f"final_seg_{idx}.mp3"
                temp_files_to_clean.extend([draft_seg_path, final_seg_path])

                asyncio.run(generate_edge_audio(trans_text, voice_code, draft_seg_path, rate="+0%"))
                if not os.path.exists(draft_seg_path):
                    continue

                draft_clip = AudioFileClip(draft_seg_path)
                natural_duration = draft_clip.duration
                draft_clip.close()

                speed_ratio = natural_duration / original_duration
                percentage_offset = int((speed_ratio - 1) * 100)
                percentage_offset = max(min(percentage_offset, 100), -50)
                rate_string = f"+{percentage_offset}%" if percentage_offset >= 0 else f"{percentage_offset}%"

                asyncio.run(generate_edge_audio(trans_text, voice_code, final_seg_path, rate=rate_string))
                if not os.path.exists(final_seg_path):
                    continue

                seg_clip = AudioFileClip(final_seg_path)
                seg_clip = seg_clip.set_start(start_time)
                
                translated_audio_clips.append(seg_clip)
                audio_clips_to_close.append(seg_clip)

            if not translated_audio_clips:
                st.error("No valid translatable audio found to generate a dub.")
                st.stop()

            st.info("Muxing audio layers back into chronological structure...")
            composite_voiceover = CompositeAudioClip(translated_audio_clips)
            audio_clips_to_close.append(composite_voiceover)

            final_video = video.set_audio(composite_voiceover)
            final_video.write_videofile(final_video_path, codec="libx264", audio_codec="aac", logger=None)

            video.close()
            for clip in audio_clips_to_close:
                try: clip.close()
                except: pass

            st.success("Translation complete!")

            with open(final_video_path, "rb") as f:
                st.download_button(
                    label="📥 Download Translated Video",
                    data=f,
                    file_name="translated_timestamp_video.mp4",
                    mime="video/mp4"
                )
            temp_files_to_clean.append(final_video_path)

        except Exception as e:
            st.error(f"Timeline Processing Fault: {str(e)}")

        finally:
            for path in temp_files_to_clean:
                if os.path.exists(path) and path != final_video_path:
                    try: os.remove(path)
                    except: pass
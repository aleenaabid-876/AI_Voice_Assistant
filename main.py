import os
import io
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS

load_dotenv()

# Streamlit App UI Setup
st.set_page_config(page_title="AI Voice Agent", page_icon="🎙️")
st.title("🎙️ AI Voice Assistant")
st.write("Record or upload your audio to talk with the AI Voice Agent.")

api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("Please configure your GROQ_API_KEY in Streamlit Secrets or .env file.")
    st.stop()

groq_client = Groq(api_key=api_key)

# Audio Upload Section (Streamlit Built-in Frontend)
audio_file = st.file_uploader("Upload an audio file (.webm, .mp3, .wav)", type=["webm", "mp3", "wav"])

if audio_file is not None:
    if st.button("Process Audio & Respond"):
        with st.spinner("Processing your voice..."):
            try:
                # Read audio file bytes
                audio_bytes = audio_file.read()
                audio_io = io.BytesIO(audio_bytes)
                audio_io.name = "input.webm"
                
                # 1. Speech-to-Text via Groq Whisper
                transcription = groq_client.audio.transcriptions.create(
                    file=audio_io,
                    model="whisper-large-v3",
                    language="en"
                )
                user_text = transcription.text
                
                if user_text.strip():
                    st.subheader("👨‍💻 You Said:")
                    st.write(user_text)
                    
                    # 2. Text LLM Completion via Llama 3.1
                    completion = groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a professional voice agent. Provide answers under two short sentences."},
                            {"role": "user", "content": user_text}
                        ],
                        temperature=0.6
                    )
                    ai_response = completion.choices[0].message.content
                    
                    st.subheader("🤖 AI Response:")
                    st.write(ai_response)
                    
                    # 3. Text-to-Speech via gTTS
                    tts = gTTS(text=ai_response, lang='en', slow=False)
                    mp3_fp = io.BytesIO()
                    tts.write_to_fp(mp3_fp)
                    mp3_fp.seek(0)
                    
                    # Play Audio response directly on web UI
                    st.subheader("🔊 Listen to Response:")
                    st.audio(mp3_fp, format="audio/mp3")
                else:
                    st.error("Could not understand the audio. Please try again.")
                    
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")
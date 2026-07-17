import os
import io
import streamlit as st
from groq import Groq
from gtts import gTTS

# 1. Page Configuration (Premium Dark Theme Theme Set)
st.set_page_config(page_title="VoiceAI Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 2. Modern Cyberpunk CSS Styling Injection (No Blank Frames)
st.markdown("""
    <style>
        /* Hide default Streamlit clutter */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Dark Gradient Background matching original theme */
        .stApp {
            background: radial-gradient(circle at 50% 120%, #0e172e 0%, #060a13 70%) !important;
            color: #f8fafc !important;
        }
        
        /* Custom Glass Panels */
        .glass-panel {
            background: rgba(13, 22, 43, 0.45);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 20px;
        }
        
        /* Dynamic Chat Bubbles */
        .user-bubble {
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.2);
            padding: 12px 16px;
            border-radius: 16px 16px 0px 16px;
            max-w-xl;
            margin-left: auto;
            margin-bottom: 10px;
            text-align: right;
        }
        .ai-bubble {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 12px 16px;
            border-radius: 16px 16px 16px 0px;
            max-w-xl;
            margin-right: auto;
            margin-bottom: 10px;
        }
        
        /* Aura Ring Pulse Simulator */
        .aura-circle {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            background: #090d16;
            border: 2px solid #6366f1;
            box-shadow: 0 0 30px rgba(99, 102, 241, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Keys Validation
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
groq_client = Groq(api_key=api_key)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----------------------------------------------------
# 4. APP LAYOUT DESIGN (Columns Architecture)
# ----------------------------------------------------
left_col, right_col = st.columns([1, 2.5])

with left_col:
    st.markdown("""
        <div class="glass-panel">
            <span style="font-size: 11px; font-weight: bold; color: #818cf8; background: rgba(99,102,241,0.15); padding: 4px 10px; border-radius: 99px;">SYSTEMS V2.5</span>
            <h1 style="font-size: 24px; margin-top: 15px; font-weight: 700;">Voice Interface</h1>
            <hr style="border-color: rgba(255,255,255,0.05); margin: 15px 0;">
            <p style="font-size: 13px; color: #94a3b8; line-height: 1.6;">
                Left control deck active. Press the microphone button below to record your voice. The intelligence core will automatically execute the query.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Secure Native Audio Recorder Input
    audio_file = st.audio_input("🎤 Record Voice Query")

with right_col:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <span style="height: 10px; width: 10px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981;"></span>
            <span style="font-size: 12px; font-weight: 600; text-transform: uppercase; color: #10b981; tracking: 1px;">System Engine Ready</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Processing Pipeline Trigger
    if audio_file:
        try:
            audio_bytes = audio_file.read()
            audio_io = io.BytesIO(audio_bytes)
            audio_io.name = "input.wav"
            
            # STT Processing
            transcription = groq_client.audio.transcriptions.create(
                file=audio_io,
                model="whisper-large-v3",
                language="en"
            )
            user_text = transcription.text
            
            if user_text.strip():
                # Llama Inference Brain
                completion = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a professional voice agent. Provide answers under two short sentences."},
                        {"role": "user", "content": user_text}
                    ],
                    temperature=0.6
                )
                ai_response = completion.choices[0].message.content
                
                # Append to history state
                st.session_state.chat_history.append({"user": user_text, "ai": ai_response})
                
                # Audio Autoplay block creation
                tts = gTTS(text=ai_response, lang='en', slow=False)
                mp3_fp = io.BytesIO()
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)
                st.audio(mp3_fp, format="audio/mp3", autoplay=True)
                
        except Exception as e:
            st.error(f"Engine Alert: {str(e)}")

    # Main Visual Display (Show Aura if empty, else show chat)
    if not st.session_state.chat_history:
        st.markdown("""
            <div style="padding: 60px 0; text-align: center;">
                <div class="aura-circle">
                    <svg style="width: 40px; height: 40px; color: #818cf8;" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                    </svg>
                </div>
                <p style="font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 2px; margin-top: 15px; font-weight: 600;">Core Module Aura</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Render clean log container blocks securely
        for chat in st.session_state.chat_history:
            st.markdown(f"""
                <div class="user-bubble">
                    <p style="font-size: 11px; font-weight: bold; color: #818cf8; margin-bottom: 2px;">User</p>
                    <p style="font-size: 14px; color: #e2e8f0; margin: 0;">{chat['user']}</p>
                </div>
                <div class="ai-bubble">
                    <p style="font-size: 11px; font-weight: bold; color: #34d399; margin-bottom: 2px;">Voice AI Engine</p>
                    <p style="font-size: 14px; color: #e2e8f0; margin: 0;">{chat['ai']}</p>
                </div>
            """, unsafe_allow_html=True)
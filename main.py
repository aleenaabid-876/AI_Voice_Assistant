import os
import io
import base64
import streamlit as st
from groq import Groq
from gtts import gTTS

# 1. Page Configuration
st.set_page_config(page_title="VoiceAI Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 2. Hide Streamlit Main Elements
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding: 0px !important;}
    </style>
""", unsafe_allow_html=True)

# 3. Keys Setup
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
groq_client = Groq(api_key=api_key)

# Session states for maintaining chat logs across rerun triggers
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ----------------------------------------------------
# 4. STREAMLIT NATIVE AUDIO PROCESSING
# ----------------------------------------------------
st.sidebar.title("Audio Controller Bypass")
audio_file = st.sidebar.audio_input("Record Voice Query Here")

if audio_file:
    try:
        audio_bytes = audio_file.read()
        audio_io = io.BytesIO(audio_bytes)
        audio_io.name = "input.wav"
        
        # Whisper STT
        transcription = groq_client.audio.transcriptions.create(
            file=audio_io,
            model="whisper-large-v3",
            language="en"
        )
        user_text = transcription.text
        
        if user_text.strip():
            # Llama Core Brain
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional voice agent. Provide answers under two short sentences."},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.6
            )
            ai_response = completion.choices[0].message.content
            
            # Save history
            st.session_state.chat_history.append({"user": user_text, "ai": ai_response})
            
            # Autoplay Response Voice (TTS)
            tts = gTTS(text=ai_response, lang='en', slow=False)
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            
            # Audio response block auto-trigger
            st.sidebar.audio(mp3_fp, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.sidebar.error(f"Engine Error: {str(e)}")

# Generate Dynamic Bubbles from History inside HTML injection
chat_bubbles_html = ""
for chat in st.session_state.chat_history:
    time_str = "Just Now"
    chat_bubbles_html += f"""
    <div class="flex flex-col items-end space-y-1">
        <div class="bg-indigo-500/10 border border-indigo-500/20 px-4 py-3 rounded-2xl rounded-tr-none max-w-md">
            <p class="text-xs font-bold text-indigo-400 mb-1">User</p>
            <p class="text-sm text-slate-200 leading-relaxed">{chat['user']}</p>
        </div>
        <span class="text-[9px] text-slate-600 px-1">{time_str}</span>
    </div>
    <div class="flex flex-col items-start space-y-1">
        <div class="bg-white/5 border border-white/10 px-4 py-3 rounded-2xl rounded-tl-none max-w-md shadow-sm">
            <p class="text-xs font-bold text-emerald-400 mb-1">Voice AI Engine</p>
            <p class="text-sm text-slate-200 leading-relaxed">{chat['ai']}</p>
        </div>
        <span class="text-[9px] text-slate-600 px-1">{time_str}</span>
    </div>
    """

# Fix the condition before passing it into f-string to avoid the specifier error
avatar_visibility = "hidden" if chat_bubbles_html else ""
log_visibility = "" if chat_bubbles_html else "hidden"

# ----------------------------------------------------
# 5. AAPKA ORIGINAL PREMIUM CYBERPUNK INTERFACE
# ----------------------------------------------------
custom_cyberpunk_ui = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoiceAI Intelligence Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-main: #060a13;
            --card-surface: rgba(13, 22, 43, 0.45);
            --border-glow: rgba(99, 102, 241, 0.15);
            --neon-cyan: #06b6d4;
            --neon-indigo: #6366f1;
            --neon-emerald: #10b981;
            --neon-rose: #f43f5e;
        }}
        body {{
            background: radial-gradient(circle at 50% 120%, #0e172e 0%, var(--bg-main) 70%);
            color: #f8fafc;
            font-family: 'Inter', system-ui, sans-serif;
            height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
            display: flex;
            overflow: hidden;
        }}
        .glass-panel {{
            background: var(--card-surface);
            backdrop-filter: blur(16px) saturate(120%);
            border: 1px solid rgba(255, 255, 255, 0.04);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            border-radius: 24px;
        }}
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(255, 255, 255, 0.1); border-radius: 99px; }}
    </style>
</head>
<body class="flex p-5 space-x-5">

    <div class="w-80 glass-panel p-6 flex flex-col justify-between border border-white/5">
        <div class="space-y-6">
            <div>
                <span class="text-xs font-bold uppercase tracking-widest text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-full">Systems v2.1</span>
                <h1 class="text-2xl font-bold mt-3 text-slate-100">Voice Interface</h1>
            </div>
            <div class="space-y-3 bg-white/5 p-4 rounded-xl border border-white/5">
                <h3 class="text-xs font-bold uppercase text-slate-400 tracking-wider">Quick Directives</h3>
                <p class="text-xs text-slate-300 leading-relaxed">
                    Use the native sidebar controller recorder to capture audio directly into the secure cloud stack.
                </p>
            </div>
        </div>
        <div class="flex items-center justify-between text-xs text-slate-500 border-t border-white/5 pt-4">
            <span>Terminal State</span>
            <span class="font-mono text-indigo-400">ONLINE</span>
        </div>
    </div>

    <div class="flex-1 flex flex-col justify-between glass-panel p-8 relative border border-white/5">
        <div class="absolute top-6 left-8 flex items-center space-x-3 bg-white/5 px-4 py-2 rounded-full border border-white/5">
            <span class="h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-[0_0_10px_#10b981]" id="statusDot"></span>
            <span id="statusText" class="text-xs font-semibold uppercase tracking-wider text-emerald-400">System Ready</span>
        </div>

        <div class="flex-1 flex flex-col items-center justify-center overflow-hidden my-6">
            <div id="avatarContainer" class="flex flex-col items-center justify-center {avatar_visibility}">
                <div class="w-36 h-36 rounded-full glass-panel flex items-center justify-center border border-white/10" id="avatarRing">
                    <div class="w-28 h-28 rounded-full bg-slate-900/80 flex items-center justify-center border border-white/5 relative overflow-hidden">
                        <svg class="w-12 h-12 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                        </svg>
                    </div>
                </div>
                <p class="text-xs text-slate-500 mt-4 tracking-widest uppercase font-semibold">Core Module Aura</p>
            </div>

            <div id="conversationLog" class="w-full max-w-2xl space-y-4 overflow-y-auto max-h-full px-2 {log_visibility}">
                {chat_bubbles_html}
            </div>
        </div>

        <div class="border-t border-white/5 pt-6 flex justify-between items-center">
            <div class="bg-white/5 px-4 py-2 rounded-xl border border-white/5">
                <p class="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Session Frame Time</p>
                <p class="text-lg font-mono font-bold text-slate-200">ACTIVE</p>
            </div>
            <p class="text-xs text-indigo-300">Use Left Sidebar mic controller for 100% cloud delivery</p>
        </div>
    </div>
</body>
</html>
"""

# Render Full Interface App View
st.html(f'<iframe srcdoc="{base64.b64encode(custom_cyberpunk_ui.encode()).decode()}" width="100%" height="850px" style="border:none;"></iframe>')
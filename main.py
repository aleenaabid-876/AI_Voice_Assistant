import os
import io
import base64
import streamlit as st
from groq import Groq
from gtts import gTTS

# 1. Page Configuration (Full screen cyberpunk view)
st.set_page_config(page_title="VoiceAI Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 2. Hide Streamlit Elements (Sahi argument ke sath taake error na aaye)
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {padding: 0px !important;}
        iframe {display: block; width: 100vw; height: 100vh; border: none;}
    </style>
""", unsafe_allow_html=True)

# 3. Streamlit Cloud Key Setup
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
groq_client = Groq(api_key=api_key)

# 4. Streamlit Queries & Custom Backend Routing
if "action" in st.query_params:
    action = st.query_params["action"]
    
    if action == "process-audio":
        try:
            audio_file = st.files.get("file")
            if audio_file:
                audio_bytes = audio_file.read()
                audio_io = io.BytesIO(audio_bytes)
                audio_io.name = "input.webm"
                
                # Speech-to-Text via Groq Whisper
                transcription = groq_client.audio.transcriptions.create(
                    file=audio_io,
                    model="whisper-large-v3",
                    language="en"
                )
                user_text = transcription.text
                
                if not user_text.strip():
                    st.json({"error": "Empty transcription"})
                    st.stop()
                    
                # LLM Brain via Llama 3.1
                completion = groq_client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a professional voice agent. Provide answers under two short sentences."},
                        {"role": "user", "content": user_text}
                    ],
                    temperature=0.6
                )
                ai_response = completion.choices[0].message.content
                
                st.json({"user_text": user_text, "ai_response": ai_response})
                st.stop()
        except Exception as e:
            st.json({"error": str(e)})
            st.stop()
            
    elif action == "tts":
        try:
            text = st.query_params.get("text", "")
            if text:
                tts = gTTS(text=text, lang='en', slow=False)
                mp3_fp = io.BytesIO()
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)
                
                st.write(mp3_fp.read(), mime="audio/mp3")
                st.stop()
        except Exception as e:
            st.stop()

# ----------------------------------------------------
# 5. AAPKA ASLI PREMIUM CYBERPUNK INTERFACE (HTML + CSS + JS)
# ----------------------------------------------------

custom_cyberpunk_ui = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoiceAI Intelligence Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #060a13;
            --card-surface: rgba(13, 22, 43, 0.45);
            --border-glow: rgba(99, 102, 241, 0.15);
            --neon-cyan: #06b6d4;
            --neon-indigo: #6366f1;
            --neon-emerald: #10b981;
            --neon-rose: #f43f5e;
        }

        body {
            background: radial-gradient(circle at 50% 120%, #0e172e 0%, var(--bg-main) 70%);
            color: #f8fafc;
            font-family: 'Inter', system-ui, sans-serif;
            height: 100vh;
            margin: 0;
            padding: 20px;
            box-sizing: border-box;
            display: flex;
            overflow: hidden;
        }

        .glass-panel {
            background: var(--card-surface);
            backdrop-filter: blur(16px) saturate(120%);
            -webkit-backdrop-filter: blur(16px) saturate(120%);
            border: 1px solid rgba(255, 255, 255, 0.04);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            border-radius: 24px;
        }

        .state-idle {
            box-shadow: 0 0 30px -5px rgba(148, 163, 184, 0.1);
            border-color: rgba(148, 163, 184, 0.2);
        }

        .state-listening {
            box-shadow: 0 0 40px -5px rgba(16, 185, 129, 0.35);
            border-color: var(--neon-emerald) !important;
        }

        .state-thinking {
            box-shadow: 0 0 40px -5px rgba(245, 158, 11, 0.35);
            border-color: #f59e0b !important;
        }

        .state-speaking {
            box-shadow: 0 0 40px -5px rgba(99, 102, 241, 0.4);
            border-color: var(--neon-indigo) !important;
        }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 99px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }

        @keyframes slow-orbit {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .spin-slow { animation: slow-orbit 12s linear infinite; }
    </style>
</head>
<body class="flex p-5 space-x-5">

    <!-- LEFT DIRECTIVES PANEL -->
    <div class="w-80 glass-panel p-6 flex flex-col justify-between border border-white/5">
        <div class="space-y-6">
            <div>
                <span class="text-xs font-bold uppercase tracking-widest text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-full">Systems v2.1</span>
                <h1 class="text-2xl font-bold mt-3 text-slate-100">Voice Interface</h1>
            </div>
            <div class="space-y-3 bg-white/5 p-4 rounded-xl border border-white/5">
                <h3 class="text-xs font-bold uppercase text-slate-400 tracking-wider">Quick Directives</h3>
                <p class="text-xs text-slate-300 leading-relaxed">
                    Initiate a connection to converse. Tap <span class="text-emerald-400 font-semibold">Start Call</span> and voice queries continuously.
                </p>
            </div>
        </div>
        <div class="flex items-center justify-between text-xs text-slate-500 border-t border-white/5 pt-4">
            <span>Terminal State</span>
            <span class="font-mono text-indigo-400">ONLINE</span>
        </div>
    </div>

    <!-- MAIN DISPLAY DASHBOARD -->
    <div class="flex-1 flex flex-col justify-between glass-panel p-8 relative border border-white/5">
        
        <!-- STATUS INDICATOR DOT & TEXT -->
        <div class="absolute top-6 left-8 flex items-center space-x-3 bg-white/5 px-4 py-2 rounded-full border border-white/5" id="statusContainer">
            <span class="h-2.5 w-2.5 rounded-full bg-slate-500 transition-all duration-300 shadow-[0_0_10px_rgba(255,255,255,0.2)]" id="statusDot"></span>
            <span id="statusText" class="text-xs font-semibold uppercase tracking-wider text-slate-400">Ready</span>
        </div>

        <!-- CORE INTERFACE LOG/AVATAR -->
        <div class="flex-1 flex flex-col items-center justify-center overflow-hidden my-6">
            <div id="avatarContainer" class="flex flex-col items-center justify-center transition-all duration-500">
                <div class="w-36 h-36 rounded-full glass-panel flex items-center justify-center border border-white/10 state-idle transition-all duration-500 ease-out" id="avatarRing">
                    <div class="w-28 h-28 rounded-full bg-slate-900/80 flex items-center justify-center border border-white/5 relative overflow-hidden group">
                        <svg class="w-12 h-12 text-indigo-400 transition-transform duration-300 group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                        </svg>
                    </div>
                </div>
                <p class="text-xs text-slate-500 mt-4 tracking-widest uppercase font-semibold animate-pulse">Core Module Aura</p>
            </div>

            <div id="conversationLog" class="w-full max-w-2xl space-y-4 overflow-y-auto max-h-full px-2 hidden"></div>
        </div>

        <!-- LOWER DASHBOARD TIMERS AND ACTIONS -->
        <div class="border-t border-white/5 pt-6 flex justify-between items-center">
            <div class="bg-white/5 px-4 py-2 rounded-xl border border-white/5">
                <p class="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Session Frame Time</p>
                <p class="text-lg font-mono font-bold text-slate-200" id="timer">00:00:00</p>
            </div>

            <div class="flex space-x-3">
                <button id="startBtn" class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-200 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)] transform active:scale-95">
                    Start Call
                </button>
                <button id="endBtn" disabled class="bg-rose-500/10 text-rose-400 border border-rose-500/20 px-6 py-3 rounded-xl font-semibold text-sm opacity-40 cursor-not-allowed transition-all duration-200 transform active:scale-95">
                    End Call
                </button>
                <button id="resetBtn" class="bg-white/5 hover:bg-white/10 text-slate-300 border border-white/5 px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-200 transform active:scale-95">
                    Clear Workspace
                </button>
            </div>
        </div>
    </div>

    <!-- AUDIO CORE ENGINE LOGIC -->
    <script>
        let mediaRecorder;
        let audioChunks = [];
        let timerInterval;
        let totalSeconds = 0;
        let isRecordingLoop = false;

        const startBtn = document.getElementById('startBtn');
        const endBtn = document.getElementById('endBtn');
        const resetBtn = document.getElementById('resetBtn');
        const statusText = document.getElementById('statusText');
        const statusDot = document.getElementById('statusDot');
        const avatarRing = document.getElementById('avatarRing');
        const conversationLog = document.getElementById('conversationLog');
        const avatarContainer = document.getElementById('avatarContainer');
        const timerDisplay = document.getElementById('timer');

        function changeAppState(state, message) {
            statusText.innerText = message;
            statusText.className = "text-xs font-semibold uppercase tracking-wider ";
            statusDot.className = "h-2.5 w-2.5 rounded-full transition-all duration-300 ";
            avatarRing.className = "w-36 h-36 rounded-full glass-panel flex items-center justify-center border transition-all duration-500 ease-out ";

            if (state === 'listening') {
                statusText.classList.add('text-emerald-400');
                statusDot.classList.add('bg-emerald-400', 'shadow-[0_0_12px_#10b981]');
                avatarRing.classList.add('state-listening');
            } else if (state === 'thinking') {
                statusText.classList.add('text-amber-400');
                statusDot.classList.add('bg-amber-400', 'shadow-[0_0_12px_#f59e0b]');
                avatarRing.classList.add('state-thinking', 'spin-slow');
            } else if (state === 'speaking') {
                statusText.classList.add('text-indigo-400');
                statusDot.classList.add('bg-indigo-400', 'shadow-[0_0_12px_#6366f1]');
                avatarRing.classList.add('state-speaking');
            } else {
                statusText.classList.add('text-slate-400');
                statusDot.classList.add('bg-slate-500');
                avatarRing.classList.add('state-idle');
            }
        }

        function startTimer() {
            totalSeconds = 0;
            clearInterval(timerInterval);
            timerInterval = setInterval(() => {
                totalSeconds++;
                let hrs = String(Math.floor(totalSeconds / 3600)).padStart(2, '0');
                let mins = String(Math.floor((totalSeconds % 3600) / 60)).padStart(2, '0');
                let secs = String(totalSeconds % 60).padStart(2, '0');
                timerDisplay.innerText = hrs + ":" + mins + ":" + secs;
            }, 1000);
        }

        startBtn.onclick = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                isRecordingLoop = true;
                
                startBtn.disabled = true;
                startBtn.classList.add('opacity-40', 'cursor-not-allowed');
                endBtn.disabled = false;
                endBtn.classList.remove('opacity-40', 'cursor-not-allowed');
                endBtn.classList.add('hover:bg-rose-500/20', 'hover:shadow-[0_0_20px_rgba(244,63,94,0.15)]');
                
                startTimer();
                streamVoiceCapturePacket();
            } catch (err) {
                alert("Active peripheral voice capture clearance is required.");
            }
        };

        function streamVoiceCapturePacket() {
            if (!isRecordingLoop) return;
            audioChunks = [];
            changeAppState('listening', 'Monitoring Audio');
            mediaRecorder.start();

            setTimeout(() => {
                if (mediaRecorder.state === "recording") mediaRecorder.stop();
            }, 4500);

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                if (isRecordingLoop) await submitPayloadToServer(audioBlob);
            };

            mediaRecorder.ondataavailable = (event) => audioChunks.push(event.data);
        }

        async function submitPayloadToServer(blob) {
            changeAppState('thinking', 'Analyzing Context');
            const formData = new FormData();
            formData.append('file', blob);

            try {
                const response = await fetch('/?action=process-audio', { method: 'POST', body: formData });
                const data = await response.json();

                if (response.ok && data.user_text) {
                    pushChatBubble(data.user_text, data.ai_response);
                    await dispatchVoiceSynthesis(data.ai_response);
                } else {
                    streamVoiceCapturePacket();
                }
            } catch (err) {
                streamVoiceCapturePacket();
            }
        }

        async function dispatchVoiceSynthesis(text) {
            changeAppState('speaking', 'Synthesizing Response');
            try {
                const response = await fetch('/?action=tts&text=' + encodeURIComponent(text), { method: 'POST' });
                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                const audio = new Audio(audioUrl);
                
                audio.onended = () => {
                    if (isRecordingLoop) streamVoiceCapturePacket();
                };
                audio.play();
            } catch (err) {
                streamVoiceCapturePacket();
            }
        }

        function pushChatBubble(user, ai) {
            avatarContainer.classList.add('hidden');
            conversationLog.classList.remove('hidden');
            
            const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

            conversationLog.innerHTML += `
                <div class="flex flex-col items-end space-y-1">
                    <div class="bg-indigo-500/10 border border-indigo-500/20 px-4 py-3 rounded-2xl rounded-tr-none max-w-md">
                        <p class="text-xs font-bold text-indigo-400 mb-1">User</p>
                        <p class="text-sm text-slate-200 leading-relaxed">${user}</p>
                    </div>
                    <span class="text-[9px] text-slate-600 px-1">${timeString}</span>
                </div>
                <div class="flex flex-col items-start space-y-1">
                    <div class="bg-white/5 border border-white/10 px-4 py-3 rounded-2xl rounded-tl-none max-w-md shadow-sm">
                        <p class="text-xs font-bold text-emerald-400 mb-1">Voice AI Engine</p>
                        <p class="text-sm text-slate-200 leading-relaxed">${ai}</p>
                    </div>
                    <span class="text-[9px] text-slate-600 px-1">${timeString}</span>
                </div>
            `;
            conversationLog.scrollTop = conversationLog.scrollHeight;
        }

        endBtn.onclick = () => {
            isRecordingLoop = false;
            clearInterval(timerInterval);
            if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
            changeAppState('idle', 'Connection Terminated');
            
            startBtn.disabled = false;
            startBtn.classList.remove('opacity-40', 'cursor-not-allowed');
            endBtn.disabled = true;
            endBtn.className = "bg-rose-500/10 text-rose-400 border border-rose-500/20 px-6 py-3 rounded-xl font-semibold text-sm opacity-40 cursor-not-allowed transition-all duration-200 transform active:scale-95";
        };

        resetBtn.onclick = () => location.reload();
    </script>
</body>
</html>
"""

# 6. Injection Layer (Embedding Custom Premium UI safely into Streamlit)
st.components.v1.html(custom_cyberpunk_ui, height=900, scrolling=False)
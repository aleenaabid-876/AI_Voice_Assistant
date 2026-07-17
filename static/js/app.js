let mediaRecorder;
let socket;
let timerInterval;
let totalSeconds = 0;

const startBtn = document.getElementById('startBtn');
const endBtn = document.getElementById('endBtn');
const resetBtn = document.getElementById('resetBtn');
const statusText = document.getElementById('statusText');
const statusDot = document.getElementById('statusDot');
const avatarRing = document.getElementById('avatarRing');
const conversationLog = document.getElementById('conversationLog');
const avatarContainer = document.getElementById('avatarContainer');
const timerDisplay = document.getElementById('timer');

// Premium Component Aesthetics Transition Manager (UNCHANGED)
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
        timerDisplay.innerText = `${hrs}:${mins}:${secs}`;
    }, 1000);
}

startBtn.onclick = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // Connect to WebSocket Server
        socket = new WebSocket(`ws://${window.location.host}/ws/stream`);
        
        socket.onopen = () => {
            startTimer();
            startBtn.disabled = true;
            startBtn.classList.add('opacity-40', 'cursor-not-allowed');
            endBtn.disabled = false;
            endBtn.classList.remove('opacity-40', 'cursor-not-allowed');
            endBtn.classList.add('hover:bg-rose-500/20', 'hover:shadow-[0_0_20px_rgba(244,63,94,0.15)]');
            
            // Start recording in timeslices (e.g., every 4 seconds chunks)
            mediaRecorder = new MediaRecorder(stream);
            changeAppState('listening', 'Monitoring Audio');
            
            mediaRecorder.ondataavailable = async (event) => {
                if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
                    changeAppState('thinking', 'Analyzing Context');
                    const arrayBuffer = await event.data.arrayBuffer();
                    socket.send(arrayBuffer);
                }
            };
            
            // Record in 4-second blocks continuously
            mediaRecorder.start(4000); 
        };

        socket.onmessage = async (event) => {
            const data = JSON.parse(event.data);
            pushChatBubble(data.user_text, data.ai_response);
            
            // Play Streamed TTS Response
            changeAppState('speaking', 'Synthesizing Response');
            const audioBytes = new Uint8Array(data.audio.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
            const audioBlob = new Blob([audioBytes], { type: 'audio/mp3' });
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            
            audio.onended = () => {
                changeAppState('listening', 'Monitoring Audio');
            };
            audio.play();
        };

    } catch (err) {
        alert("Active peripheral voice capture clearance is required.");
    }
};

function pushChatBubble(user, ai) {
    avatarContainer.classList.add('hidden');
    conversationLog.classList.remove('hidden');
    
    const timeString = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    conversationLog.innerHTML += `
        <div class="flex flex-col items-end space-y-1 animate-[fadeIn_0.3s_ease-out]">
            <div class="bg-indigo-500/10 border border-indigo-500/20 px-4 py-3 rounded-2xl rounded-tr-none max-w-md">
                <p class="text-xs font-bold text-indigo-400 mb-1">User</p>
                <p class="text-sm text-slate-200 leading-relaxed">${user}</p>
            </div>
            <span class="text-[9px] text-slate-600 px-1">${timeString}</span>
        </div>
        <div class="flex flex-col items-start space-y-1 animate-[fadeIn_0.3s_ease-out]">
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
    clearInterval(timerInterval);
    if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
    if (socket) socket.close();
    
    changeAppState('idle', 'Connection Terminated');
    
    startBtn.disabled = false;
    startBtn.classList.remove('opacity-40', 'cursor-not-allowed');
    endBtn.disabled = true;
    endBtn.className = "bg-rose-500/10 text-rose-400 border border-rose-500/20 px-6 py-3 rounded-xl font-semibold text-sm opacity-40 cursor-not-allowed transition-all duration-200 transform active:scale-95";
};

resetBtn.onclick = () => location.reload();
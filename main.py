import os
import io
import asyncio
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from groq import Groq
from gtts import gTTS

load_dotenv()

app = FastAPI(title="AI Voice Agent Backend")
app.mount("/static", StaticFiles(directory="static"), name="static")

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def get_ui(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive raw audio chunk from frontend
            data = await websocket.receive_bytes()
            
            if not data:
                continue
                
            audio_file = io.BytesIO(data)
            audio_file.name = "input.wav"
            
            # 1. Speech-to-Text via Groq Whisper
            transcription = groq_client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                language="en"
            )
            user_text = transcription.text
            
            if not user_text.strip():
                continue

            # 2. Text LLM Completion
            completion = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional voice agent. Provide answers under two short sentences."},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.6
            )
            ai_response = completion.choices[0].message.content

            # 3. Generate TTS Audio bytes
            tts = gTTS(text=ai_response, lang='en', slow=False)
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            tts_bytes = mp3_fp.read()

            # Send data back to client as JSON containing texts and audio bytes
            await websocket.send_json({
                "user_text": user_text,
                "ai_response": ai_response,
                "audio": tts_bytes.hex() # Sending as hex string for easy JS parsing
            })

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
import os
import io
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
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

@app.post("/process-audio")
async def process_audio(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "input.webm"
        
        # 1. Speech-to-Text via Groq Whisper
        transcription = groq_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3",
            language="en"
        )
        user_text = transcription.text
        if not user_text.strip():
            return JSONResponse(content={"error": "Empty transcription"}, status_code=400)

        # 2. Text LLM Completion via updated Active Llama 3.1 Architecture
        completion = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a professional voice agent. Provide answers under two short sentences."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.6
        )
        ai_response = completion.choices[0].message.content

        return JSONResponse(content={"user_text": user_text, "ai_response": ai_response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/tts")
async def text_to_speech(text: str = Form(...)):
    tts = gTTS(text=text, lang='en', slow=False)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return StreamingResponse(mp3_fp, media_type="audio/mp3")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
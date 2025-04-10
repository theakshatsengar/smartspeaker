from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
import os
import requests
from pydantic import BaseModel
import base64
from groq import Groq

app = FastAPI()

# ENV VARS (Set these before deploying)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Init Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Model for chat input
class ChatRequest(BaseModel):
    prompt: str

@app.post("/chat")
def chat_with_groq(data: ChatRequest):
    try:
        completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": data.prompt}],
            model="llama-3.3-70b-versatile",
            stream=False
        )
        return {"reply": completion.choices[0].message.content}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/stt")
def speech_to_text(audio: UploadFile = File(...)):
    try:
        audio_content = audio.file.read()
        b64_audio = base64.b64encode(audio_content).decode("utf-8")

        stt_response = requests.post(
            f"https://speech.googleapis.com/v1/speech:recognize?key={GOOGLE_API_KEY}",
            json={
                "config": {
                    "encoding": "LINEAR16",
                    "languageCode": "en-US"
                },
                "audio": {
                    "content": b64_audio
                }
            }
        )
        stt_result = stt_response.json()
        transcript = stt_result['results'][0]['alternatives'][0]['transcript']
        return {"text": transcript}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

class TTSRequest(BaseModel):
    text: str

@app.post("/tts")
def text_to_speech(data: TTSRequest):
    try:
        response = requests.post(
            f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_API_KEY}",
            json={
                "input": {"text": data.text},
                "voice": {"languageCode": "en-US", "name": "en-US-Wavenet-D"},
                "audioConfig": {"audioEncoding": "MP3"}
            }
        )
        tts_audio = response.json()['audioContent']
        audio_bytes = base64.b64decode(tts_audio)
        return StreamingResponse(iter([audio_bytes]), media_type="audio/mpeg")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import os
import requests
import base64
from groq import Groq

app = FastAPI()

# ENV VARS
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# Init Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

@app.post("/process_audio")
async def process_audio(audio: UploadFile = File(...)):
    try:
        # 1. Speech to Text (STT)
        audio_content = await audio.read()
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
        user_text = stt_result['results'][0]['alternatives'][0]['transcript']

        # 2. LLM Response (Groq)
        completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a smart speaker assistant. "
                        "Always respond in very short, precise sentences. "
                        "Be clear, friendly, and to-the-point. "
                        "Avoid long explanations. Act like a helpful AI."
                    )
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            model="llama-3-3-70b-versatile",
            stream=False
        )
        llm_reply = completion.choices[0].message.content

        # 3. Text to Speech (TTS)
        tts_response = requests.post(
            f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_API_KEY}",
            json={
                "input": {"text": llm_reply},
                "voice": {"languageCode": "en-US", "name": "en-US-Wavenet-D"},
                "audioConfig": {"audioEncoding": "MP3"}
            }
        )
        tts_audio = tts_response.json()['audioContent']
        audio_bytes = base64.b64decode(tts_audio)

        return StreamingResponse(
            iter([audio_bytes]),
            media_type="audio/mpeg",
            headers={
                "X-User-Text": user_text,
                "X-LLM-Reply": llm_reply
            }
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

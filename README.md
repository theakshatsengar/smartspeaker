# smartspeaker

# Smart Speaker Backend

This is a FastAPI backend for a smart speaker project. It handles:
- ✅ Speech-to-text using Google Cloud STT
- 🧠 Text generation via Groq's LLaMA-3 API
- 🔊 Text-to-speech using Google Cloud TTS

## 🔧 Features
- `/stt`: Converts uploaded `.wav` audio to text.
- `/chat`: Sends the transcribed text to Groq LLM and receives a response.
- `/tts`: Converts the response text into an MP3 audio file.

## 🌍 API Endpoints

### `POST /stt`
**Request**: Upload `.wav` file (LINEAR16 format).

**Response**:
```json
{
  "text": "Recognized speech here"
}
```

---

### `POST /chat`
**Request**:
```json
{
  "prompt": "Explain the importance of fast language models"
}
```

**Response**:
```json
{
  "reply": "Fast language models are important because..."
}
```

---

### `POST /tts`
**Request**:
```json
{
  "text": "Hello, how can I help you?"
}
```

**Response**: Streamed MP3 audio response.

---

## 🛠️ Deployment on Render

1. Push the code to a GitHub repo.
2. Go to [https://render.com](https://render.com) → "New +" → Web Service
3. Connect your repo.
4. **Build Command:**
```
pip install -r requirements.txt
```
5. **Start Command:**
```
uvicorn main:app --host 0.0.0.0 --port 10000
```
6. **Environment Variables:**
```
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
```

---

## 📦 Requirements
Install dependencies:
```
pip install -r requirements.txt
```

---

## 🎤 ESP32 Integration
You can now:
- Record audio on the ESP32
- Send it via HTTP to `/stt`
- Send received text to `/chat`
- Convert response using `/tts`
- Play the MP3 stream on a Bluetooth or wired speaker

---

Built with ❤️ by Akshat and Zuck

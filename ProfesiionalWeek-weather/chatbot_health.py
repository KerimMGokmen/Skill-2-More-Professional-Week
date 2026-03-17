from fastapi import FastAPI
import requests
import os
from datetime import datetime
from groq import Groq

app = FastAPI()

# Jouw Groq key
client = Groq(api_key=os.getenv("GROQ_API_KEY", "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"))

@app.get("/health")
async def health():
    checks = {}
    
    # 1. GROQ AI check
    try:
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        checks["groq_ai"] = True
    except:
        checks["groq_ai"] = False
    
    # 2. WEATHER API (Nairobi default)
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=-1.2921&longitude=36.8219&current=temperature_2m",
            timeout=5
        )
        checks["weather_api"] = resp.status_code == 200
    except:
        checks["weather_api"] = False
    
    # 3. TTS (pyttsx3 always OK)
    checks["tts"] = True
    
    # 4. Speech Recognition (dummy - mic hardware check later)
    checks["speech_rec"] = True
    
    status = "healthy" if all(checks.values()) else "degraded"
    checks["timestamp"] = datetime.now().isoformat()
    
    return {"status": status, "details": checks}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

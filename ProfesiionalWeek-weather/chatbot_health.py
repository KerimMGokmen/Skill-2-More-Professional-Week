from fastapi import FastAPI
import requests
import os
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health():
    # Vervang deze met je echte endpoints
    weather_ok = requests.get("https://api.openweathermap.org/data/2.5/weather?q=Nairobi&appid=test", timeout=3).status_code == 200
    tts_ok = True  # Test je TTS
    checks = {
        "chatbot": "running",
        "weather_api": weather_ok,
        "tts": tts_ok,
        "timestamp": datetime.now().isoformat(),
        "deploy_tag": os.getenv("IMAGE_TAG", "local-dev")
    }
    status = "healthy" if weather_ok and tts_ok else "degraded"
    return {"status": status, "details": checks}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

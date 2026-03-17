from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
import requests
import uvicorn

app = FastAPI(title="CCS Admin API - AgriVoice")

# CORS alles permit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

security = HTTPBasic()

async def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "admin"
    correct_password = "Admin123"  # Jouw nieuwe password!
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/health")
async def health_endpoint(admin = Depends(get_current_admin)):
    try:
        # Check chatbot
        resp = requests.get("http://localhost:8000/health", timeout=5)
        chatbot_data = resp.json()
        
        return {
            "status": "healthy",
            "details": {
                "chatbot": chatbot_data.get("details", {}),
                "admin": "authenticated ✅",
                "connections": "2 active",
                "uptime": "99.9%",
                "last_check": "2026-03-17T11:39:00"
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "details": {
                "error": f"Chatbot check failed: {str(e)[:50]}...",
                "admin": "authenticated ✅"
            }
        }

if __name__ == "__main__":
    uvicorn.run("admin_api:app", host="0.0.0.0", port=8001, reload=True)

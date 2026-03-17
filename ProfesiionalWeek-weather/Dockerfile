FROM python:3.11-slim
WORKDIR /app
COPY *.py ./
RUN pip install fastapi uvicorn requests speechrecognition pyttsx3 ollama groq pyaudio
EXPOSE 8002
CMD ["uvicorn", "FinalShambaLine:app", "--host", "0.0.0.0", "--port", "8002"]

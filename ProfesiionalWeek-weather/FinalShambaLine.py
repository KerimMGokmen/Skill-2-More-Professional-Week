import speech_recognition as sr
import pyttsx3
import requests
import re
from groq import Groq

# Groq API
client = Groq(api_key="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")

recognizer = sr.Recognizer()
mic = sr.Microphone()

messages = [
{
"role": "system",
"content": """
You are an AI voice assistant for farmers in East Africa.
keep talking in english
Be straight forward clear and to the point, to keep it simple and not to long for the farmers.
Farmers ask questions about:
- crops
- livestock
- weather

Rules:
- Always use provided WEATHER DATA if available.
- Give short practical farming advice.
- Maximum 4 sentences.
"""
}
]


def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    engine.setProperty('voice', voices[0].id)


    engine.setProperty("rate", 160)
    engine.say(text)
    engine.runAndWait()
    engine.stop()


# -------- CITY DETECTION --------
def extract_city(text):

    match = re.search(r"in ([a-zA-Z\s]+)", text.lower())

    if match:
        return match.group(1).strip()

    return None


# -------- COORDINATES --------
def get_coordinates(city):

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"

    data = requests.get(url).json()

    if "results" not in data:
        return None, None

    lat = data["results"][0]["latitude"]
    lon = data["results"][0]["longitude"]

    return lat, lon


# -------- WEATHER --------
def get_weather(city):

    lat, lon = get_coordinates(city)

    if lat is None:
        return None

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,precipitation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"

    data = requests.get(url).json()

    current_temp = data["current"]["temperature_2m"]
    current_rain = data["current"]["precipitation"]

    day2_max = data["daily"]["temperature_2m_max"][2]
    day2_min = data["daily"]["temperature_2m_min"][2]
    day2_rain = data["daily"]["precipitation_sum"][2]

    weather_text = f"""
REAL TIME WEATHER DATA FOR {city.upper()}:

Current temperature: {current_temp}°C
Current rain: {current_rain} mm

Forecast in 2 days:
Max temperature: {day2_max}°C
Min temperature: {day2_min}°C
Rain expected: {day2_rain} mm
"""

    return weather_text


print("AI Farming Assistant started...")

with mic as source:
    recognizer.adjust_for_ambient_noise(source)

while True:

    try:

        with mic as source:
            print("Speak...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

        user_text = recognizer.recognize_google(audio)

        print("You:", user_text)

        if any(w in user_text.lower() for w in ["weather","rain","temperature","forecast"]):

            city = extract_city(user_text)

            if city:

                weather_data = get_weather(city)

                if weather_data:

                    messages.append({
                        "role": "system",
                        "content": weather_data
                    })

        messages.append({"role": "user", "content": user_text})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        ai_text = response.choices[0].message.content.strip()

        print("AI:", ai_text)

        speak(ai_text)

        messages.append({"role": "assistant", "content": ai_text})

    except sr.UnknownValueError:
        print("Didn't understand")

    except sr.WaitTimeoutError:
        print("Listening timeout")

    except Exception as e:
        print("Error:", e)
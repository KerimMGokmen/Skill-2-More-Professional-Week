import speech_recognition as sr
import pyttsx3
import ollama
import requests

API_KEY = "d28e8fd2180d48ffae4220536261603"

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def get_weather(city):
    url = f"https://api.worldweatheronline.com/premium/v1/weather.ashx?key={API_KEY}&q={city}&format=json&num_of_days=7"
    try:
        data = requests.get(url).json()
        return data["data"]
    except:
        return None

def generate_weather_sentence(city, day_index, user_question):
    weather_data = get_weather(city)
    if not weather_data:
        return "Sorry, I could not fetch the weather."

    day = weather_data["weather"][day_index]
    date = day["date"]
    desc = day["hourly"][4]["weatherDesc"][0]["value"]
    min_temp = day["mintempC"]
    max_temp = day["maxtempC"]

    # Laat AI zelf een korte zin maken met alleen de relevante info
    prompt = f"""
You are an AI assistant.
User asked: "{user_question}"

Weather data: date={date}, description={desc}, min_temp={min_temp}, max_temp={max_temp}, city={city}

Generate ONE friendly, natural sentence in English summarizing the forecast.
Include only date, city, weather description, and min/max temperature.
Do not add advice or other commentary.
"""
    response = ollama.chat(model="phi3", messages=[{"role":"user","content":prompt}])
    return response["message"]["content"]

recognizer = sr.Recognizer()
mic = sr.Microphone()

messages = [
    {"role": "system", "content": "You are a helpful AI assistant that answers shortly in English."}
]

print("AI assistant started...")
print("Type a message or press ENTER to speak.")

with mic as source:
    recognizer.adjust_for_ambient_noise(source)

while True:

    user_text = input("\nYou (type or press ENTER to speak): ")

    if user_text.strip() == "":
        try:
            with mic as source:
                print("Listening...")
                audio = recognizer.listen(source)
            user_text = recognizer.recognize_google(audio, language="en-US")
            print("You:", user_text)
        except sr.UnknownValueError:
            print("Could not understand you.")
            continue
    else:
        print("You:", user_text)

    # 🌦️ Weather detection
    if "weather" in user_text.lower() or "temperature" in user_text.lower():
        words = user_text.split()
        city = words[-1]  # simpel: laatste woord als stad

        # Bepaal dag_index: AI kan dit ook doen via een klein prompt, maar hier simpel
        day_index = 0
        if "tomorrow" in user_text.lower():
            day_index = 1
        elif "in 2 days" in user_text.lower() or "day after tomorrow" in user_text.lower():
            day_index = 2
        elif "in 3 days" in user_text.lower():
            day_index = 3
        elif "in 4 days" in user_text.lower():
            day_index = 4

        ai_text = generate_weather_sentence(city, day_index, user_text)

        print("AI:", ai_text)
        speak(ai_text)
        continue

    # Normale AI conversatie
    messages.append({"role": "user", "content": user_text})
    response = ollama.chat(model="phi3", messages=messages)
    ai_text = response["message"]["content"]
    print("AI:", ai_text)
    speak(ai_text)
    messages.append({"role": "assistant", "content": ai_text})
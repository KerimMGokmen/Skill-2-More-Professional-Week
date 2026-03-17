import speech_recognition as sr
import pyttsx3
import ollama


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()


recognizer = sr.Recognizer()
mic = sr.Microphone()

messages = [
    {"role": "system", "content": "You are a helpful AI assistant that answers shortly in English."}
]

print("AI assistant started...")

with mic as source:
    recognizer.adjust_for_ambient_noise(source)

while True:
    try:
        with mic as source:
            print("\nSpeak now...")
            audio = recognizer.listen(source)

        user_text = recognizer.recognize_google(audio, language="en-US")
        print("You:", user_text)

        messages.append({"role": "user", "content": user_text})

        response = ollama.chat(
            model="phi3",
            messages=messages
        )

        ai_text = response["message"]["content"]

        print("AI:", ai_text)

        speak(ai_text)

        messages.append({"role": "assistant", "content": ai_text})

    except sr.UnknownValueError:
        print("Could not understand you.")

import speech_recognition as sr

def voice_to_text():
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("Speak now...")
            audio = recognizer.listen(source, timeout=5)

        text = recognizer.recognize_google(audio)
        return text

    except:
        return "Voice not detected properly."
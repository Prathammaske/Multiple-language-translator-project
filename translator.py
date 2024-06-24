from flask import Flask, render_template, request
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

app = Flask(__name__)


def get_supported_gtts_languages():
    from gtts.lang import tts_langs
    return tts_langs()

SUPPORTED_GTTs_LANGUAGES = get_supported_gtts_languages()

def recognize_speech_from_mic(recognizer, microphone):
    """Transcribe speech recorded from `microphone`."""
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)

    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        response["error"] = "Unable to recognize speech"

    return response

def translate_text(text, target_language):
    """Translate text to the target language."""
    if target_language == 'zh':
        target_language = 'zh-CN'  # default to Simplified Chinese
    translated = GoogleTranslator(source='auto', target=target_language).translate(text)
    return translated

def text_to_speech(text, language):
    """Convert text to speech in the given language."""
    tts = gTTS(text=text, lang=language)
    save_path = os.path.join("static", "output.mp3")
    tts.save(save_path)
    os.system("start " + save_path)  # For Windows, use "start"; for macOS, use "open"; for Linux, use "xdg-open".

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target_language = request.form['target_language']
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        response = recognize_speech_from_mic(recognizer, microphone)

        if response["success"]:
            transcription = response['transcription']
            if not transcription:
                error = "No speech detected. Please try again."
                return render_template('index.html', languages=SUPPORTED_GTTs_LANGUAGES, error=error)
            
            translated_text = translate_text(transcription, target_language)
            text_to_speech(translated_text, target_language)
            return render_template('result.html', original=transcription, translated=translated_text)
        else:
            error = response["error"]
            return render_template('index.html', languages=SUPPORTED_GTTs_LANGUAGES, error=error)
    else:
        return render_template('index.html', languages=SUPPORTED_GTTs_LANGUAGES)


if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, request, jsonify
from flask_cors import CORS
import speech_recognition as sr
from gtts import gTTS
import io
import base64
from pydub import AudioSegment
from text import Textify

app = Flask(__name__)
CORS(app)

recognizer = sr.Recognizer()
translator = Textify()

def get_language_code(lang_name):
    LANGUAGE_CODES = {
        'english': 'en', 'spanish': 'es', 'french': 'fr',
        'german': 'de', 'japanese': 'ja', 'hindi': 'hi',
        'en': 'en', 'es': 'es', 'fr': 'fr', 'de': 'de',
        'ja': 'ja', 'hi': 'hi'
    }
    return LANGUAGE_CODES.get(lang_name.lower(), 'en')

@app.route("/translate-audio", methods=["POST"])
def translate_audio():
    try:
        file = request.files['audio']
        print(f"Received audio file: {file.filename}, Content-Type: {file.content_type}")

        source_lang = request.form.get("source_lang", "auto")
        target_lang = request.form.get("target_lang", "en")
        print(f"Source lang: {source_lang}, Target lang: {target_lang}")

        audio = AudioSegment.from_file(file, format="webm")
        audio_wav = io.BytesIO()
        audio.export(audio_wav, format="wav")
        audio_wav.seek(0)
        print("Converted audio to WAV")

        with sr.AudioFile(audio_wav) as source:
            audio_data = recognizer.record(source)
            print("Audio data extracted")

            try:
                text = recognizer.recognize_google(audio_data)
                print(f"Recognized: {text}")
            except sr.UnknownValueError:
                print("Speech not recognized.")
                return jsonify({"recognized_text": "Could not recognize speech."}), 200

        try:
            basic = translator.translate_text(text, target_lang, source_lang)
            enhanced = translator.enhance_translation_with_ai(text, basic)
        except Exception as e:
            print("Translation error:", e)
            basic = f"(fallback) Translated: {text}"
            enhanced = basic

        tts = gTTS(text=enhanced, lang=get_language_code(target_lang))
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_b64 = base64.b64encode(fp.read()).decode("utf-8")

        return jsonify({
            "recognized_text": text,
            "basic_translation": basic,
            "ai_translation": enhanced,
            "audio_base64": audio_b64
        })

    except Exception as e:
        print("Unhandled error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

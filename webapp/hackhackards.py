from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from aitranslator import Textify
import os
import tempfile
import speech_recognition as sr
from gtts import gTTS
import base64
import io

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/textify")
def textify():
    return render_template("textify.html")

@app.route("/audiomac_real")
def audiomac_real():
    return render_template("audiomac_real.html")

@app.route("/audiomac")
def audiomac():
    return render_template("audiomac.html")

@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.get_json()
        text = data['text']
        srcLangCode = getLanguageCode(data['srcLang'])
        destLangCode = getLanguageCode(data['destLang'])
        translator = Textify()
        translatedText = translator.translate_text(text, destLangCode, srcLangCode)
        return jsonify({"translatedText": translatedText}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/translate-audio", methods=["POST"])
def translate_audio():
    try:
        # Get audio file from request
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
            
        audio_file = request.files["audio"]
        source_lang = request.form.get("source_lang", "auto")
        target_lang = request.form.get("target_lang", "en")

        # Create a temporary file to save the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            # Save the uploaded file
            audio_file.save(temp_file.name)
            
            # Initialize recognizer
            recognizer = sr.Recognizer()
            
            # Convert speech to text
            with sr.AudioFile(temp_file.name) as source:
                # Adjust for ambient noise and record
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.record(source)
                
                try:
                    # Attempt speech recognition
                    text = recognizer.recognize_google(audio_data, language=source_lang)
                except sr.UnknownValueError:
                    return jsonify({"error": "Could not understand the audio"}), 400
                except sr.RequestError as e:
                    return jsonify({"error": f"Speech recognition error: {str(e)}"}), 500

        # Clean up temporary file
        os.unlink(temp_file.name)

        # Translate the text
        translator = Textify()
        basic_translation = translator.translate_text(text, target_lang, source_lang)
        enhanced_translation = translator.enhance_translation_with_ai(text, basic_translation)

        # Convert translated text to speech
        tts = gTTS(text=enhanced_translation, lang=target_lang)
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        audio_b64 = base64.b64encode(audio_fp.read()).decode("utf-8")

        return jsonify({
            "recognized_text": text,
            "basic_translation": basic_translation,
            "ai_translation": enhanced_translation,
            "audio_base64": audio_b64
        })

    except Exception as e:
        print("Error in translate_audio:", str(e))
        return jsonify({"error": str(e)}), 500

def getLanguageCode(language):
    languageDict = {
        'English': 'en', 
        'French': 'fr', 
        'German': 'de', 
        'Hindi': 'hi', 
        'Japanese': 'ja',
        'Spanish': 'es'
    }
    return languageDict.get(language, "en")  # Default to English if language is not found

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
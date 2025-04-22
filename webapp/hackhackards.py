from flask import Flask, request, jsonify, render_template
from aitranslator import Textify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/textify")
def textify():
    return render_template("textify.html")

@app.route("/translate", methods=["POST"])
def translate():
    print(request.headers)
    data = request.get_json()
    print(data)
    text = data['text']
    srcLangCode = getLanguageCode(data['srcLang'])
    destLangCode = getLanguageCode(data['destLang'])
    translatedText = Textify.translate_text(Textify, text, destLangCode, srcLangCode)
    data = {
        "translatedText": translatedText
    }
    return jsonify(data),200

def getLanguageCode(language):
    languageDict  = {
        'English': 'en', 
        'French': 'fr', 
        'German': 'de', 
        'Hindi': 'hi', 
        'Japanese': 'ja',
        'Spanish': 'es'}
    return languageDict[language]

if __name__ == "__main__":
    app.run(host='0.0.0.0')

'''
const translations = {
                    "English": {
                        "Spanish": "Este es un texto traducido del inglés al español.",
                        "French": "Ceci est un texte traduit de l'anglais vers le français.",
                        "German": "Dies ist ein Text, der vom Englischen ins Deutsche übersetzt wurde.",
                        "Japanese": "これは英語から日本語に翻訳されたテキストです。"
                    },
                    "Spanish": {
                        "English": "This is a text translated from Spanish to English.",
                        "French": "Ceci est un texte traduit de l'espagnol vers le français.",
                        "German": "Dies ist ein Text, der vom Spanischen ins Deutsche übersetzt wurde.",
                        "Japanese": "これはスペイン語から日本語に翻訳されたテキストです。"
                    },
                    "French": {
                        "English": "This is a text translated from French to English.",
                        "Spanish": "Este es un texto traducido del francés al español.",
                        "German": "Dies ist ein Text, der vom Französischen ins Deutsche übersetzt wurde.",
                        "Japanese": "これはフランス語から日本語に翻訳されたテキストです。"
                    },
                    "German": {
                        "English": "This is a text translated from German to English.",
                        "Spanish": "Este es un texto traducido del alemán al español.",
                        "French": "Ceci est un texte traduit de l'allemand vers le français.",
                        "Japanese": "これはドイツ語から日本語に翻訳されたテキストです。"
                    },
                    "Japanese": {
                        "English": "This is a text translated from Japanese to English.",
                        "Spanish": "Este es un texto traducido del japonés al español.",
                        "French": "Ceci est un texte traduit du japonais vers le français.",
                        "German": "Dies ist ein Text, der vom Japanischen ins Deutsche übersetzt wurde."
                    }
                };
                
                if (translations[fromLang] && translations[fromLang][toLang]) {
                    return translations[fromLang][toLang];
                }
'''
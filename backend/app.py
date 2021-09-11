from flask import Flask, request
import requests
from google.cloud import speech


app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

@app.route('/search/<item>')
def search(item):
    r = requests.get('https://fakestoreapi.com/products')
    data = r.json()
    newData = [obj for obj in data if item.lower() in obj['title'].lower()]
    return str(newData)

@app.route('/audio', methods=['POST'])
def stt():
    client = speech.SpeechClient()
    file1 = request.data
    audio = speech.RecognitionAudio(content=file1)

    config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
    sample_rate_hertz=16000,
    language_code="pt-BR",
    )
    response = client.recognize(config=config, audio=audio)
    stringzona = str([result.alternatives[0].transcript for result in response.results])
    payload = {
        "voice": {
            "ssmlGender": "NEUTRAL",
            "languageCode": "pt-BR",
            "name": "lol"
        },
        "audioConfig": {
            "audioEncoding": "OGG_OPUS",
            "pitch": 0
        },
        "input": {
            "text": "compra tv com vapi"
        }
    }
    a = requests.post('https://texttospeech.googleapis.com/v1/text:synthesize?key=[INSERT_KEY_HERE]', data=payload)
    data2 = a.text
    if "televisão" in stringzona.lower():
        r = requests.get('http://localhost:5000/search/monitor')
        data = r.text
    return data2
    return str([result.alternatives[0].transcript for result in response.results])
    #return str(file1)

if __name__ == '__main__':
    app.run(debug=True)


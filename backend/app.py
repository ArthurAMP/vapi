from flask import Flask, request
import requests
from google.cloud import speech, texttospeech_v1, texttospeech, translate_v2
import os 
import json
import ast
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
    client1 = texttospeech_v1.TextToSpeechClient()
    file1 = request.data
    audio = speech.RecognitionAudio(content=file1)

    config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
    sample_rate_hertz=16000,
    language_code="pt-BR",
    )
    response = client.recognize(config=config, audio=audio)
    stringzona = str([result.alternatives[0].transcript for result in response.results])

    if "televisão" in stringzona.lower():
        r = requests.get('http://localhost:5000/search/monitor')
        data = r.text
        data = data.replace("[", "")
        data = data.replace("]", "")
        data2 = ast.literal_eval(data)
        data2 = data2["title"]
    data2 = str(data2)
    target = 'pt'
    client2 = translate_v2.Client()
    data2 = client2.translate(
        data2,
        target_language=target
    )
    ttstext = str(data2["translatedText"])
    synthesis_input = texttospeech_v1.SynthesisInput(text=ttstext)
    voice = texttospeech_v1.VoiceSelectionParams(
        language_code='pt-BR',
        ssml_gender=texttospeech_v1.SsmlVoiceGender.FEMALE
    )
    audio_config = texttospeech_v1.AudioConfig(
        audio_encoding=texttospeech_v1.AudioEncoding.OGG_OPUS
    )
    response1 = client1.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    with open('audio file1.ogg', 'wb') as output1:
        output1.write(response1.audio_content)
    
    return str(data2["translatedText"])
    return str([result.alternatives[0].transcript for result in response.results])
    #return str(file1)

if __name__ == '__main__':
    app.run(debug=True)


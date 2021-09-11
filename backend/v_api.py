#verificar local_url
#verificar google auth
#verificar bitrate

from flask import Flask, request, send_from_directory
import os, requests
from google.cloud import speech, texttospeech_v1, translate_v2
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
local_url = 'http://cdf4-177-12-40-19.ngrok.io/upload'
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../../auth.json'

def search(item):
    r = requests.get('https://fakestoreapi.com/products')
    data = r.json()
    products = [obj for obj in data if item.lower() in obj['title'].lower()]
    return products

@app.route('/')
def home():
    return "<h1> Hello, World!"

@app.route('/upload')
def uploaded_file():
    upload_folder = "C:/Users/kimka/Google Drive/!Projetos/Programação/vapi/vapi/backend"
    
    return send_from_directory(upload_folder,
                               'audio_file2.ogg')

@app.route('/whatsapp-request', methods=['POST'])
def whatsapp_request():
    incoming_msg = request.values

    #Twilio Answer
    response = MessagingResponse()
    print(response)
    response_msg = response.message()

    if incoming_msg.get('NumMedia', '') == '0':
        response_msg.body('Só recebo áudios')
        print("enviei mensagem de texto")

    elif incoming_msg.get('NumMedia', '') == '1':
        print("Recebi um áudio")
        
        # Speech to text
        speech_client = speech.SpeechClient()

        response_media = requests.get(incoming_msg.get('MediaUrl0', ''))
        audio_bytes = response_media._content
        
        # with open('audio_file1.ogg', 'wb') as output1:
        #     output1.write(audio_bytes)
        
        incoming_audio = speech.RecognitionAudio(content = audio_bytes)

        config_speech = speech.RecognitionConfig(
                                        encoding = speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
                                        sample_rate_hertz = 16000,
                                        language_code = "pt-BR",
        )
        raw_text_response = speech_client.recognize(config = config_speech, audio = incoming_audio)
        text_response = str([result.alternatives[0].transcript for result in raw_text_response.results])

        print("texto: ", text_response)
        
        #Pesquisa de itens
        if "televisão" in text_response.lower():
            search_result = search('monitor')
            search_result_title = search_result[0]["title"]

            print("vou traduzir")

            #Traduzir
            target_language = 'pt'
            translate_client = translate_v2.Client()

            search_result_title_translated = translate_client.translate(
                search_result_title,
                target_language = target_language
            )

            #tts
            tts_client = texttospeech_v1.TextToSpeechClient()
            ttstext = str(search_result_title_translated["translatedText"])

            synthesis_input = texttospeech_v1.SynthesisInput(text = ttstext)
            
            voice_config = texttospeech_v1.VoiceSelectionParams(
                language_code = 'pt-BR',
                ssml_gender = texttospeech_v1.SsmlVoiceGender.FEMALE
            )

            audio_config = texttospeech_v1.AudioConfig(
                audio_encoding = texttospeech_v1.AudioEncoding.OGG_OPUS
            )

            response_tts = tts_client.synthesize_speech(
                input = synthesis_input,
                voice = voice_config,
                audio_config = audio_config
            )

            with open('audio_file2.ogg', 'wb') as audio_response:
                audio_response.write(response_tts.audio_content)

            response_msg.media(local_url)
    
    print(response)
    return str(response)

def main():
    print(" ----- autenticado -----")
    app.run(debug = True)

if __name__ == '__main__':
    main()

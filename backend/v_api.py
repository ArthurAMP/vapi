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

users = {}
users["0"] = {
    'step': 0,
    'cart': 0
}
with open('users.txt', 'w') as outfile:
    json.dump(users, outfile)

@app.route('/whatsapp-request', methods=['POST'])
def whatsapp_request():
    carrinho = 0
    passo = 0
    flag = 0
    incoming_msg = request.values
    number = incoming_msg.get("from", "null")
    
    if number in users.keys():
        carrinho = users[number]["cart"]
        passo = users[number]["step"]
    else:
        users[number] = {
            'step': 0,
            'cart': 0
        }
                    
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
        if passo==0 and "compra" in text_response.lower():
            synthesis("Oi, tudo bem? Sou a vapi! Em qual loja você quer comprar?")
            response_msg.media(local_url)
            passo = 1
            users[number]["step"] = passo
        elif passo==1 and "x" in text_response.lower():
            synthesis("Você escolheu comprar na x, qual produto você quer comprar")
            response_msg.media(local_url)
            passo = 2
            users[number]["step"] = passo
        elif passo==2 and "monitor" in text_response.lower():
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
            ttstext = "nós temos: "
            ttstext += str(search_result_title_translated["translatedText"])
            synthesis(ttstext)
            response_msg.media(local_url)
            passo = 3
            users[number]["step"] = passo
        elif passo == 3 and "detalhes" in text_response.lower():
            search_result = search('monitor')
            search_result_title = search_result[0]["description"]

            print("vou traduzir")

            #Traduzir
            target_language = 'pt'
            translate_client = translate_v2.Client()

            search_result_title_translated = translate_client.translate(
                search_result_title,
                target_language = target_language
            )

            #tts
            ttstext = "detalhes: "
            ttstext += str(search_result_title_translated["translatedText"])
            synthesis(ttstext)
            response_msg.media(local_url)
        elif passo == 3 and "custo" in text_response.lower():
            ttstext = "o monitor custa 999,99 reais"
            synthesis(ttstext)
            response_msg.media(local_url)
        elif passo == 3 and "adicionar" in text_response.lower():
            users[number]["cart"] += 999.99
            passo += 1
            users[number]["step"] = passo
            ttstext = "O monitor foi adicionado ao carrinho. Seu carrinho custa: " + str(users[number]["cart"]) + "reais. Quer continuar comprando?"
            synthesis(ttstext)
            response_msg.media(local_url)
        elif passo == 4 and "não" in text_response.lower():
            ttstext = "Vamos finalizar a compra. Qual o método de pagamento?"
            passo += 1
            users[number]["step"] = passo
            synthesis(ttstext)
            response_msg.media(local_url)
        elif passo == 4 and "quero" in text_response.lower():
            passo = 2
            users[number]["step"] = passo
            ttstext = "OK. O que você quer comprar agora?"
            synthesis(ttstext)
            response_msg.media(local_url)

        elif passo == 5 and "chave" in text_response.lower():
            ttstext = "A chave pix é 999999999999, pague o valor de " + str(users[number]["cart"]) + " reais para essa chave pix para completar a compra."
            users[number]["cart"] = 0
            users[number]["step"] = 0
            synthesis(ttstext)
            response_msg.media(local_url)
        elif "cancela" in text_response.lower():
            ttstext = "compra cancelada"
            users[number]["cart"] = 0
            users[number]["step"] = 0
            synthesis(ttstext)
            response_msg.media(local_url)
        else:
            ttstext = "desculpa não entendi o que você quis dizer."
            synthesis(ttstext)
            response_msg.media(local_url)
    print(response)
    print("passo:" + str(passo))
    return str(response)

def synthesis(ttstext):
    tts_client = texttospeech_v1.TextToSpeechClient()

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

def main():
    print(" ----- autenticado -----")
    app.run(debug = True)

if __name__ == '__main__':
    main()

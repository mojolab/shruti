'''
Simple Flask API to receive a message as a JSON object and return a response as a JSON object.
'''
messagelogfile="/opt/shrutibot-appdata/samyog-data/messagelog"
from datetime import datetime
from flask import Flask, request, jsonify
import io, os
from google.cloud import speech
import requests
app = Flask(__name__)
hostname="http://192.168.1.11"
@app.route('/listener', methods=["POST"])
def listener():
     input_json = request.get_json(force=True) 
     input_json['timercvd'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")    
     # send input_json to processing function
     print(input_json)
     result = process_message(input_json)
     with open(messagelogfile, 'a') as f:
         f.write(str(result) + '\n')
     return jsonify(result)


def get_mojogoat_response(message):
    resturl=":5001/listener"
    try:
        response=requests.post(hostname+resturl,json=message)
        return response.json()
    except Exception as e:
        message['error']=str(e)
        return message



# Process media messages
def process_media_message(message):
    # do something with the message
    return message
 
# Process text messages
def process_text_message(message):
    # if message text starts with GOAT, then send it to mojogoat API
    if message['text'].startswith("GOAT"):
        message=get_mojogoat_response(message)
    return message


def process_message(message):
    if "media" not in message.keys() or message['media'] is None:
        message['response']="Thats strange! I am not programmed to respond to that."
        try:
            fort=os.popen("fortune").read()
            message['response']+="\n...but...here's a funny quote to make your day:\n{}".format(fort)
        except:
            pass
        message=process_text_message(message)
        return message
    # do something with the message
    if message['media'] is not None and message['media']['type']=='voice' or message['media']['type']=='audio':
        samplerate=int(os.popen("/usr/bin/ffprobe -v error -show_streams {} | grep sample_rate".format(message['media']['path'])).read().strip().split("=")[1])
        if samplerate>16000:
            samplerate=16000
        filetype = message['media']['path'].split(".")[-1]
        if filetype == 'ogg' or filetype == 'opus':
            enc=speech.RecognitionConfig.AudioEncoding.OGG_OPUS
        elif filetype == 'wav':
            enc=speech.RecognitionConfig.AudioEncoding.LINEAR16
        
        print("Encoding: {}, Sample Rate:{}".format(enc,samplerate))
        client=speech.SpeechClient()
        with io.open(message['media']['path'], 'rb') as audio_file:
            content = audio_file.read()
        audio=speech.RecognitionAudio(content=content)
        config=speech.RecognitionConfig(
            encoding=enc,
            sample_rate_hertz=samplerate,
            # use_enhanced=True,
            # A model must be specified to use enhanced model.
            # model="phone_call",
            language_code='hi-IN')
        response = client.recognize(config=config, audio=audio)
        # Add the transcript from response.results.alternatives to message['googlespeech]
        if response.results:
            message['googlespeech'] = {
                                        "transcript":response.results[0].alternatives[0].transcript,
                                        "confidence":response.results[0].alternatives[0].confidence
                                        } 
            #message['rasaresponse']=get_rasa_response(message['sender'],message['googlespeech']['transcript'])[0]['text']  
        else:
            print(response)
    return message


def get_rasa_response(username,message_text,hostname="http://172.17.0.1"):
    resturl=":5005/webhooks/rest/webhook"
    jsondata={}
    jsondata['sender']=username
    jsondata['message']=message_text
    try:
        response=requests.post(hostname+resturl,json=jsondata)
        return response.json()
    except Exception as e:
        jsondata['error']=str(e)
        return jsondata


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')





    

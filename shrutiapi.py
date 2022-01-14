'''
Simple Flask API to receive a message as a JSON object and return a response as a JSON object.
'''
messagelogfile="../data/messagelog"
from datetime import datetime
from flask import Flask, request, jsonify
import io, os
from google.cloud import speech

app = Flask(__name__)

@app.route('/listener', methods=["POST"])
def listener():
     input_json = request.get_json(force=True) 
     input_json['timercvd'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")    
     # send input_json to processing function
     result = process_message(input_json)
     with open(messagelogfile, 'a') as f:
         f.write(str(result) + '\n')
     
     return jsonify(input_json)

def process_message(message):
    if message['media'] is None:
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
        else:
            print(response)
    return message


def get_rasa_response(username,message_text,hostname="http://localhost"):
    logger.info("Trying")
    resturl=":5005/webhooks/rest/webhook"
    jsondata={}
    jsondata['sender']=username
    jsondata['message']=message_text
    response=requests.post(hostname+resturl,json=jsondata)
    return response.json()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')





    

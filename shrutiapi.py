'''
Simple Flask API to receive a message as a JSON object and return a response as a JSON object.
'''
messagelogfile="../data/messagelog"
from datetime import datetime
from flask import Flask, request, jsonify
import io
from google.cloud import speech

app = Flask(__name__)

@app.route('/listener', methods=["POST"])
def listener():
     input_json = request.get_json(force=True) 
     input_json['timercvd'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")    
    
     with open(messagelogfile, 'a') as f:
         f.write(str(input_json) + '\n')
     # send input_json to processing function
     result = process_message(input_json)
     return jsonify(input_json)

def process_message(message):
    # do something with the message
    if message['media'] is not None and message['media']['type']=='voice':
        client=speech.SpeechClient()
        with io.open(message['media']['path'], 'rb') as audio_file:
            content = audio_file.read()
        audio=speech.RecognitionAudio(content=content)
        config=speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            sample_rate_hertz=16000,
            # use_enhanced=True,
            # A model must be specified to use enhanced model.
            # model="phone_call",
            language_code='en-IN')
        response = client.recognize(config=config, audio=audio)
        # Add the transcript from response.results.alternatives to message['googlespeech]
        if response.results:
            message['googlespeech'] = {
                                        "transcript":response.results[0].alternatives[0].transcript,
                                        "confidence":response.results[0].alternatives[0].confidence
                                        }   
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





    

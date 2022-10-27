'''
Simple Flask API to receive a message as a JSON object and return a response as a JSON object.
'''
from datetime import datetime
from flask import Flask, request, jsonify
import io, os,sys,json
from google.cloud import speech
from jinja2 import TemplatesNotFound
import requests
app = Flask(__name__)
import openai

print(sys.argv[1])

with open(sys.argv[1],'r') as f:
    apiconfig=json.load(f)

messagelogfile=apiconfig['messagelog']
print(messagelogfile)
servicelist=apiconfig['services']
mojogoathostname="http://localhost"
for service in servicelist:
    if service['servicename']=="mojogoat":
        mojogoathostname=service['servicehostname'] 


@app.route('/listener', methods=["POST"])
def listener():
     input_json = request.get_json(force=True) 
     input_json['timercvd'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")    
     # send input_json to processing function
     print(input_json)
     result = process_message(input_json)
     global messagelogfile
     with open(messagelogfile, 'a') as f:
         f.write(str(result) + '\n')
     return jsonify(result)



def process_message(message):
    message['response']={}
    print(message)
    if "media" not in message.keys() or message['media'] is None:
        print("No media")
        message=process_text_message(message)
        return message
    # do something with the message
    if message['media'] is not None and message['media']['type']=='voice' or message['media']['type']=='audio':
       message=process_audio_message(message)

    return message






# Process audio messages
def process_audio_message(message):
    # do something with the message
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
        #use_enhanced=True,
        # A model must be specified to use enhanced model.
        #model="phone_call",
        language_code='en-US')
    response = client.recognize(config=config, audio=audio)
    # Add the transcript from response.results.alternatives to message['googlespeech]
    if response.results:
        
        message['response']['googlespeech'] = {
                                    "transcript":response.results[0].alternatives[0].transcript,
                                    "confidence":response.results[0].alternatives[0].confidence
                                    } 
        
        message=process_text_message({'text':"ASKMARV "+message['response']['googlespeech']['transcript']})
    else:
        print(response)
        message['response']['googlespeech'] = str(response)
        message['response']['text']="Sorry, I didn't get that. Please try again."
    return message
 
# Process text messages
def process_text_message(message):
    # if message text starts with GOAT, then send it to mojogoat API
    message['response']={}
    if "reply_to_message" in message.keys() and message['reply_to_message'] is not None:
        message['apply_to']=message['reply_to_message']['text']
        message.pop('reply_to_message')
    if message['text'].startswith("GOAT") or message['text'].startswith("HERD"):
        message=get_mojogoat_response(message)
    if message['text'].startswith("ASKMARV"):
        string=message['text'].split("ASKMARV")[1].lstrip().rstrip()
        if "{" in string:
            content=json.loads(string)
            if "googlespeech" in content.keys():
                transcript=content['googlespeech']['transcript']
                if transcript.startswith("my name is"):
                    message['response']['text']="Hello {}".format(transcript.split("my name is")[1].lstrip().rstrip())
                else:
                    message['response']['text']=get_marv_response(transcript)
        else:
            if string.startswith("my name is"):
                message['response']['text']="Hello {}".format(string.split("my name is")[1].lstrip().rstrip())
            else:
                message['response']['text']=get_marv_response(string)
    if message['response']=={}:
        message['response']['text']="Thats strange! I am not programmed to respond to that."
        try:
            fort=os.popen("/usr/games/fortune").read()
            message['response']['text']+="\n...but...here's a funny quote to make your day:\n{}".format(fort)
        except:
            pass
    return message



def get_marv_response(message):
    marvprompt="Marv is a chatbot that reluctantly answers questions with sarcastic responses:\n\nYou: How many pounds are in a kilogram?\nMarv: This again? There are 2.2 pounds in a kilogram. Please make a note of this.\nYou: What does HTML stand for?\nMarv: Was Google too busy? Hypertext Markup Language. The T is for try to ask better questions in the future.\nYou: When did the first airplane fly?\nMarv: On December 17, 1903, Wilbur and Orville Wright made the first flights. I wish they’d come and take me away.\nYou: What is the meaning of life?\nMarv: I’m not sure. I’ll ask my friend Google.\nYou: "   
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=marvprompt+message+"\nMarv: ",
        temperature=0.5,
        max_tokens=60,
        top_p=0.3,
        frequency_penalty=0.5,
        presence_penalty=0.0    
    )
    return response.choices[0].text



def get_mojogoat_response(message):
    resturl=":5001/listener"
    try:
        response=requests.post(mojogoathostname+resturl,json=message)
        return response.json()
    except Exception as e:
        message['error']=str(e)
        return message



'''
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
'''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')





    

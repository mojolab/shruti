'''
Simple Flask API to receive a message as a JSON object and return a response as a JSON object.
'''
from datetime import date, datetime
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
     #print(input_json)
     result = process_message(input_json)
     global messagelogfile
     with open(messagelogfile, 'a') as f:
         f.write(str(result) + '\n')
     return jsonify(result)


def process_message(message):
    message['response']={}
    #print(message)
    if "media" not in message.keys() or message['media'] is None:
        print("No media")
        print(message)
        message=process_text_message(message)
        return message
    # do something with the message
    if message['media'] is not None and message['media']['type']=='voice' or message['media']['type']=='audio':
       message=process_audio_message(message)

    return message


# Process audio messages
def process_audio_message(message):
    # Extract encoding and sample rate from media file
    samplerate=int(os.popen("/usr/bin/ffprobe -v error -show_streams {} | grep sample_rate".format(message['media']['path'])).read().strip().split("=")[1])
    if samplerate>16000:
        samplerate=16000
    filetype = message['media']['path'].split(".")[-1]
    if filetype == 'ogg' or filetype == 'opus':
        enc=speech.RecognitionConfig.AudioEncoding.OGG_OPUS
    elif filetype == 'wav':
        enc=speech.RecognitionConfig.AudioEncoding.LINEAR16
    
    print("Encoding: {}, Sample Rate:{}".format(enc,samplerate))
    # Send audio file to Google Speech API
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
    # Process the response from Speech AI
    if response.results:
        filepath=os.path.split(message['media']['path'])[0]
        googlespeech = {
                            "transcript":response.results[0].alternatives[0].transcript,
                            "confidence":response.results[0].alternatives[0].confidence
                        } 
        message=process_text_message({'text':"ASKMARV "+googlespeech['transcript']})
        message['response']['googlespeech']=googlespeech
        message['response']['media']={
            "type":"audio",
            "path":get_audio(message['response']['text'],filepath)
        }
    else:
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
        if string.startswith("my name is"):
            message['response']['text']="Hello {}".format(string.split("my name is")[1].lstrip().rstrip())
        else:
            message['response']['text']=get_marv_response(string)
    if message['text'].startswith("#akslogs"):
        string=message['text'].lstrip().rstrip()#.split("ASKMARV")[1]
        if string.startswith("my name is"):
            message['response']['text']="Hello {}".format(string.split("my name is")[1].lstrip().rstrip())
        else:
            message['response']['text']=get_akslogs_response(string)+"\n\n<b><i>Entered by</b></i>:{}".format(message['sender'])
    if message['response']=={}:
        message['response']['text']="Thats strange! I am not programmed to respond to that."
        try:
            fort=os.popen("/usr/games/fortune").read()
            message['response']['text']+="\n...but...here's a funny quote to make your day:\n{}".format(fort)
        except:
            pass
    return message


def get_marv_response(message):
    with open("openaiprompts/sarcasticmarv",'r') as f:
        marvprompt=f.read()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=marvprompt+message+"\nOutput: ",
        temperature=0.5,
        max_tokens=512,
        top_p=0.3,
        frequency_penalty=0.5,
        presence_penalty=0.0    
    )
    try:
        responsejson=json.loads(response.choices[0].text)
        return responsejson
    except:
        print("returning text")
        return response.choices[0].text




def get_akslogs_response(message):
    with open("openaiprompts/akslogs",'r') as f:
        marvprompt=f.read()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
        model="text-davinci-002",
        prompt=marvprompt+message+"\nOutput: ",
        temperature=0.5,
        max_tokens=512,
        top_p=0.3,
        frequency_penalty=0.5,
        presence_penalty=0.0    
    )
    try:
        responsejson=json.loads(response.choices[0].text)
        responsetext="#AKSLOGENTRY {}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if "feeds" in responsejson.keys():
            responsetext+="<b>Feeds</b>:\n"
            for feed in responsejson['feeds']:
                responsetext+="<i>Time</i>: {}\t<i>Size</i>: {}\n\n".format(feed['time'],feed['feedsize'])
        if "meds" in responsejson.keys():
            responsetext+="<b>Meds</b>:\n"
            for med in responsejson['meds']:
                responsetext+="<i>Time</i>: {}\t<i>Med</i>: {}\n\n".format(med['time'],med['medname'])
        if "notes" in responsejson.keys():
            responsetext+="<b>Notes</b>:\n{}".format(responsejson['notes'])
        return responsetext
    except Exception as e:
        print(str(e))
        return response.choices[0].text


def get_mojogoat_response(message):
    resturl=":5001/listener"
    try:
        response=requests.post(mojogoathostname+resturl,json=message)
        return response.json()
    except Exception as e:
        message['error']=str(e)
        return message


def get_audio(text,path):
    command='espeak -w {} -v en-us "{}"'.format(os.path.join(path,"respfile.wav"),text)
    os.system(command)
    return os.path.join(path,"respfile.wav")


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





    

import requests
import json
import ast

async def handle_message(data, DB, dbRequest, output_channel, sid):
    if(data['message'].startswith('%//')):
        message = {"text": "__You intended to run a special command__" , "quick_replies": []}
        messages = [message]
    elif(dbRequest == []):
        str = "Hello "+ data['customData']['userName']+ ", we haven't met before, I'm HelpBot, and I'm here to help you on the Vericast platform."
        message1 = {"text": str , "quick_replies": []}
        message2 = {"text":"What can I do for you ?", "quick_replies": []}
        DB.insert({'userName':data['customData']['userName']})
        messages = [message1, message2]
    else:
        payload = {"sender":data["session_id"], "message":data["message"]}
        headers = {'Content-Type': "application/json",}
        r = requests.request("POST", "http://localhost:5006/webhooks/rest/webhook", data=json.dumps(payload), headers=headers)
        answer = ast.literal_eval(r.text)
        messages = convert_http_answer_to_socketio(answer)
    for message in messages:
     await output_channel._send_message(sid,message)
    return

def convert_http_answer_to_socketio(httpAnswer):
    messages = []
    messages.append("bot_uttered")
    for k in range(0, len(httpAnswer),1):
        j = {}
        j['text'] = httpAnswer[k]['text']
        j['quick_replies'] = []
        try:
            liste_bouttons = httpAnswer[k]['buttons']
            for i in range(0, len(liste_bouttons),1):
                payload = liste_bouttons[i]['payload'][1:]
                title = liste_bouttons[i]['title']
                j['quick_replies'].append({"content_type":"text","title":title,"payload":payload})
        except:
            print('')
        messages.append(j)
    return messages
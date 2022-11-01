import pytz, requests, json, os
from datetime import datetime
from flask import Flask, render_template, request

web = Flask(__name__)
key=os.environ["key"]
api=os.environ["api"]
receiver_email = [os.environ['receiver']]

def send(name, message, receivers):
    data={
        "key": key,
        "body": name,
        "subject": message,
        "mode": "normal",
        "receivers": receivers
    }
    resp = requests.post(api, data=json.dumps(data))
    return resp.text

def list_extractor(string, seperators = [", ", ",", ";", "; "]) -> list:
    string = string.strip()
    for sep in seperators:
        if sep not in string:
            continue
        string = string.split(sep)
        break
    return string

@web.route('/',methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        if name != "":
            time_zone = pytz.timezone('Europe/Stockholm')
            time = datetime.now(time_zone)
            current_date = time.strftime("%y%m%d")
            current_time = time.strftime("%H%M")

            if ("test" in name.lower()):
                receivers = name.strip()
                receivers = receivers.split(" | ")[1]
                receivers = list_extractor(receivers)
            else:
                receivers = receiver_email

            if not isinstance(receivers, list):
                receivers = [receivers]

            print(f"Recived from: {name} at {current_date} kl {current_time}")
            resp = send(name, f"VVIS {current_date} kl {current_time}", receivers)
            print("Sent")
            print(f"Response: {resp}")
    return render_template('index.html')

web.run(host='0.0.0.0', port=80)
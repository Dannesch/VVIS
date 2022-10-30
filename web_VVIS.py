import pytz
from datetime import datetime
from flask import Flask, render_template, request

web = Flask(__name__)
receiver_email = "test_mail@test.com"

def send(name, message, receivers):
    print(name, message, receivers)

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
            else:
                receivers = receiver_email

            print(f"Recived from: {name} at {current_date} kl {current_time}")
            send(name, f"VVIS {current_date} kl {current_time}", receivers)
    return render_template('index.html')

web.run(host='0.0.0.0', port=8080)
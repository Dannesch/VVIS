from __future__ import print_function
from flask import Flask, render_template, request
import webbrowser
import email, smtplib, ssl
import os
import pyautogui 
import time
import pytz
import os.path
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

web_site = Flask(__name__)
web_site.debug = True
sender_email = "dsanne75@gmail.com"
password = "rnrjdiiwsojxmqcg"

places_def = ["Karta", "Soderhall", "Sattra", "Sono", "Glugga", "Aby", "Vaddo", "Alunda", "Halkriskkarta"]
web_def = ["https://vvis.trafikverket.se/","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=224&RetX=688646&RetY=6619193", "https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=309&RetX=694731&RetY=6661526","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=238&RetX=702669&RetY=6645651","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=308&RetX=677004&RetY=6643005","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=229&RetX=671448&RetY=6627659","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=239&RetX=711061&RetY=6656764","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=306&RetX=668992&RetY=6661526","https://vvis.trafikverket.se/Functions/Slip/Slipmap.aspx"]
pyautogui.FAILSAFE = True

def Send(name, subject, places, web):
    vvis_start = True
    body = f"{name}"
    receiver_email = "do.norraroslagen@svevia.se"
    if (name == "Test"):
        receiver_email = "dschem.ds@gmail.com"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    #Screenshots
    for i in range(len(places)):
        webbrowser.open(f'{web[i]}')
        if (i == 0):
            time.sleep(1)
            pyautogui.press('f11')
            time.sleep(8)
            while vvis_start:
                try:
                    place = pyautogui.locateOnScreen('loggin.png')
                    w=place[2]/2
                    h=place[3]/2
                    x=place[0]+w
                    y=place[1]+h
                    vvis_start = False
                except:
                    vvis_start = True
            time.sleep(2)
            pyautogui.moveTo(x, y, duration=0)
            time.sleep(2)
            pyautogui.click()
        time.sleep(8)
        pyautogui.screenshot(f"{places[i]}.png")
        time.sleep(2)
    pyautogui.hotkey('alt', 'f4')

    #Attatching images to mail
    for place in places:
        filename = f"{place}.png"
        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        message.attach(part)
    text = message.as_string()

    # Log in and send mail
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
        print(f"sent to: {name}")
    
    #Delete images
    for i in range(len(places)):
        if(os.path.isfile(f"{places[i]}.png") == True):
            os.remove(f"{places[i]}.png")


@web_site.route('/',methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        age = request.form['age']
        if age != "":
            #t = []
            #s = request.form.getlist('Place')
            #print(web_def)
            #for i in places_def:
            #    if(i in s):
            #        c = places_def.index(i)
            #        t.append(web_def[c])
            tz = pytz.timezone('Europe/Stockholm')
            now = datetime.now(tz)
            date = now.strftime("%y%m%d")
            tm = now.strftime("%H%M")
            print(f"Recived from: {age} at {date} kl {tm}")
            Send(age, f"VVIS {date} kl {tm}", places_def, web_def)
    return render_template('index.html')

web_site.run(host='0.0.0.0', port=8080)

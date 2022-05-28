import smtplib, ssl
import os
import pytz
from time import sleep as delay
from playwright.sync_api import sync_playwright
from flask import Flask, render_template, request
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

web = Flask(__name__)
sender_email = "dsanne75@gmail.com"
password = "rnrjdiiwsojxmqcg"

names = ["Karta", "Soderhall", "Sattra", "Sono", "Glugga", "Aby", "Vaddo", "Alunda", "Halkriskkarta", "Textprognos"]
urls = ["https://vvis.trafikverket.se/","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=224&RetX=688646&RetY=6619193", "https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=309&RetX=694731&RetY=6661526","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=238&RetX=702669&RetY=6645651","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=308&RetX=677004&RetY=6643005","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=229&RetX=671448&RetY=6627659","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=239&RetX=711061&RetY=6656764","https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=306&RetX=668992&RetY=6661526","https://vvis.trafikverket.se/Functions/Slip/Slipmap.aspx","https://vvis.trafikverket.se/Functions/TextPrognos/TextPrognos2.aspx"]

def screenshooter():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for i in range(len(urls)):
            page.goto(urls[i])
            if i == 0:
                page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtUserName\"]").click()
                page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtUserName\"]").fill("brian.schembri@svevia.se")
                page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtUserName\"]").press("Tab")
                page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtPassWord1\"]").fill("Vagen22")
                with page.expect_navigation():
                    page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtPassWord1\"]").press("Enter")
            if names[i] == "Textprognos":
                page.locator("a[role=\"presentation\"]:has-text(\"Svealand\")").click()
                page.locator("text=Visa delprognosområde: AllaStockholms län utom RoslagskustenStockholms län, Rosl >> select").select_option("Stockholms län, Roslagskusten")
                page.locator("text=Visa delprognosområde: AllaStockholms län utom RoslagskustenStockholms län, Rosl >> #inputOK").click()
            delay(3)
            page.screenshot(path=names[i]+".png")
        browser.close()

def send(name, subject):
    body = f"{name}"
    receiver_email = "do.norraroslagen@svevia.se"
    if (name.lower() == "test"):
        receiver_email = "dschem.ds@gmail.com"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    screenshooter()

    #Attatching images to mail
    for place in names:
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
        print(f"Sent to: {name}")
    
    #Delete images
    for i in names:
        if(os.path.isfile(f"{i}.png") == True):
            os.remove(f"{i}.png")

@web.route('/',methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        if name != "":
            time_zone = pytz.timezone('Europe/Stockholm')
            time = datetime.now(time_zone)
            current_date = time.strftime("%y%m%d")
            current_time = time.strftime("%H%M")
            print(f"Recived from: {name} at {current_date} kl {current_time}")
            send(name, f"VVIS {current_date} kl {current_time}")
    return render_template('index.html')

web.run(host='0.0.0.0', port=8080)
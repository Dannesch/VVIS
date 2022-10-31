import smtplib, ssl
import os
from time import sleep
from playwright.async_api import async_playwright

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union
from enum import Enum

sender_email = os.environ['sender']
receiver_email = [os.environ['receiver']]
password = os.environ['password']
mail_server = os.environ['mail_server']
smtp_port = int(os.environ['smtp_port'])
vvis_email = os.environ['vvis_email']
vvis_password = os.environ['vvis_password']
key = os.environ['key']

app = FastAPI()
locations = {
    "Karta": "https://vvis.trafikverket.se/",
    "Soderhall": "https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=224&RetX=688646&RetY=6619193",
    "Sattra": "https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=309&RetX=694731&RetY=6661526",
    "Sono": "https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=238&RetX=702669&RetY=6645651",
    "Glugga": "https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=308&RetX=677004&RetY=6643005",
    "Aby": "https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=229&RetX=671448&RetY=6627659",
    "Vaddo": "https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=239&RetX=711061&RetY=6656764",
    "Alunda": "https://vvis.trafikverket.se/Functions/StationInfo/StationInfoPopup.aspx?Railroad=false&Term=yttempftyta&StationId=306&RetX=668992&RetY=6661526",
    "Halkriskkarta": "https://vvis.trafikverket.se/Functions/Slip/Slipmap.aspx",
    "Textprognos": "https://vvis.trafikverket.se/Functions/TextPrognos/TextPrognos2.aspx"
}

class CEnum(Enum):
    different = 'different'
    normal = 'normal'

class Send_data(BaseModel):
    key: str
    body: str
    mode: CEnum = CEnum.normal
    subject: Union[str, None] = "VVIS"
    receivers = receiver_email
    locs: Union[list, None] = ['Karta',"Soderhall","Sattra","Sono","Glugga","Aby","Vaddo","Alunda","Halkriskkarta","Textprognos"]
    locs_dict: Union[dict, None] = {}

async def screenshooter(locs):
    vvis_logged_in = False
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        for loc in locs:
            name=loc
            url=locations[loc]
            await page.goto(url)

            if "vvis.trafikverket.se" in url:
                if not vvis_logged_in:
                    await page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtUserName\"]").click()
                    await page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtUserName\"]").fill(vvis_email)
                    await page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtUserName\"]").press("Tab")
                    await page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtPassWord1\"]").fill(vvis_password)
                    async with page.expect_navigation():
                        await page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtPassWord1\"]").press("Enter")
                    vvis_logged_in = True

                if name == "Textprognos":
                    await page.locator("a[role=\"presentation\"]:has-text(\"Svealand\")").click()
                    await page.locator("text=Visa delprognosområde: AllaStockholms län utom RoslagskustenStockholms län, Rosl >> select").select_option("Stockholms län, Roslagskusten")
                    await page.locator("text=Visa delprognosområde: AllaStockholms län utom RoslagskustenStockholms län, Rosl >> #inputOK").click()

            sleep(3)
            await page.screenshot(path=name+".png")
        await browser.close()

@app.post("/send/")
async def send(data:Send_data):
    body = data.body
    subject = data.subject
    receivers = data.receivers
    locs = data.locs
    locs_dict = data.locs_dict
    mode = data.mode
    print("Request received")

    if mode == CEnum.normal:
        for i in receivers:
            locs_dict[i] = data.locs # type: ignore

    if key != data.key:
        return {    
            "data": "Wrong key",
            "finish": False
        }

    body = str(body)

    await screenshooter(locs)
    for i, j in locs_dict.items(): # type: ignore
        message = MIMEMultipart()
        message["From"] = sender_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        
        #Attatching images to mail
        for loc in j: # type: ignore
            filename = f"{loc}.png"
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
        with smtplib.SMTP_SSL(mail_server, smtp_port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, i, text)
            print(subject, "; Sent to: ", i, sep="")
    
    #Delete images
    for loc in locs: # type: ignore
        if(os.path.isfile(f"{loc}.png") == True):
            os.remove(f"{loc}.png")

    return {
        "data":{
            "body": body,
            "subject": subject,
            "receivers": receivers,
            "locs": locs
        },
        "finish": True
    }
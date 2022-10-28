import smtplib, ssl
import os
from time import sleep as delay
from playwright.sync_api import sync_playwright
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sender_email = os.environ['sender']
receiver_email = os.environ['receiver']
password = os.environ['password']
mail_server = os.environ['mail_server']
smtp_port = os.environ['smtp_port']
vvis_email = os.environ['vvis_email']
vvis_password = os.environ['vvis_password']

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

def screenshooter(locs):
    vvis_logged_in = False
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        for loc in locs:
            name=loc
            url=locations[loc]
            page.goto(url)

            if "vvis.trafikverket.se" in url:
                if not vvis_logged_in:
                    page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtUserName\"]").click()
                    page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtUserName\"]").fill(vvis_email)
                    page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtUserName\"]").press("Tab")
                    page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtPassWord1\"]").fill(vvis_password)
                    with page.expect_navigation():
                        page.locator("input[name=\"ctl00\\$ContentPlaceHolder1\\$VViSLoginControl\\$tabsAccountLogin\\$tabLogin\\$ucLoginTo\\$txtPassWord1\"]").press("Enter")
                    vvis_logged_in = True

                if name == "Textprognos":
                    page.locator("a[role=\"presentation\"]:has-text(\"Svealand\")").click()
                    page.locator("text=Visa delprognosområde: AllaStockholms län utom RoslagskustenStockholms län, Rosl >> select").select_option("Stockholms län, Roslagskusten")
                    page.locator("text=Visa delprognosområde: AllaStockholms län utom RoslagskustenStockholms län, Rosl >> #inputOK").click()

            delay(3)
            page.screenshot(path=name+".png")
        browser.close()

def is_string(string, seps = [", ", " ", "; ", ","]):
    if isinstance(string, str):
        string = string.strip()
        for sep in seps:
            if sep in string:
                string = string.split(", ")
    return string

def send(body, subject, receivers = receiver_email, locs:list = ['Karta',"Soderhall","Sattra","Sono","Glugga","Aby","Vaddo","Alunda","Halkriskkarta","Textprognos"]):
    receivers = is_string(receivers)

    body = str(body)
    message = MIMEMultipart()
    message["From"] = sender_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    screenshooter(locs)

    #Attatching images to mail
    for loc in locs:
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
        server.sendmail(sender_email, receivers, text)
        print(body)
    
    #Delete images
    for loc in locs:
        if(os.path.isfile(f"{loc}.png") == True):
            os.remove(f"{loc}.png")

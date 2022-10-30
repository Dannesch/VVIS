import requests, time
from imap_tools import MailBox

imap_port=993
mail_server="mail.schemsv.com"
password="UWH5AFMWHWkShylN9mSyBHlSNA5YysiN4dBVbHKz9RyFIm0pIEoZ3DnVILdr"
sender="vvis@schemsv.com"

def remove_old(new, old):
    for i in old:
        if i in new:
            del new[i]
    return new
while True:
    with MailBox(mail_server).login(sender, password, 'INBOX') as mailbox:
        bodies = {}
        old_len = None
        old_list = None
        for i in range(91):
            for msg in mailbox.fetch():
                if msg.from_ != "bschem67@gmail.com": continue
                bodies[msg.uid] = {
                    "text": msg.text,
                    "subject": msg.subject
                }
            if old_len != None and old_list != None and old_len < len(bodies):
                new_messages = remove_old(bodies, old_list)
            print(bodies)
            old_len = len(bodies)
            old_list = bodies
            time.sleep(20)
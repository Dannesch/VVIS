import requests, time
from imap_tools import MailBox, AND

imap_port=993
mail_server="mail.schemsv.com"
password="UWH5AFMWHWkShylN9mSyBHlSNA5YysiN4dBVbHKz9RyFIm0pIEoZ3DnVILdr"
sender="vvis@schemsv.com"

def remove_old(new, old):
    for i in old:
        if i in new:
            new.remove(i)
    return new

while True:
    with MailBox(mail_server).login(sender, password, 'INBOX') as mailbox:
        old_len = None
        old_list = None
        for i in range(91):
            bodies = []
            for msg in mailbox.fetch():
                if msg.from_ != "dschem.ds@gmail.com": continue
                bodies.append(msg.uid)
            if old_len != None and old_list != None and old_len < len(bodies):
                new_messages = remove_old(bodies, old_list)
                for i in new_messages:
                    message = list(mailbox.fetch(AND(uid=i)))[0]
                    print(message.subject)
            old_len = len(bodies)
            old_list = bodies
            print(old_len)
            time.sleep(2)
import requests, time, json, os
from imap_tools import MailBox, AND

imap_port=os.environ["imap_port"]
mail_server=os.environ["mail_server"]
password=os.environ["password"]
sender=os.environ["sender"]
key=os.environ["key"]
api=os.environ["api"]
filter_from=os.environ["filter_from"]

def remove_old(new, old):
    for i in old:
        if i in new:
            new.remove(i)
    return new

def extract_data(body:str, data):
    return body.replace("\r\n"," ").split(f"[{data}]")[1].split(f"[/{data}]")[0].strip().split(", ")

while True:
    with MailBox(mail_server).login(sender, password, 'INBOX') as mailbox:
        old_len = None
        old_list = None
        for i in range(91):
            bodies = []
            for msg in mailbox.fetch(AND(seen=False)):
                if msg.from_ != filter_from: continue
                bodies.append(msg.uid)

            if old_len != None and old_list != None and old_len < len(bodies):
                print("New Mail recieved")
                new_messages = remove_old(bodies, old_list)
                for i in new_messages:
                    recipiant_loc_list = {}
                    message = list(mailbox.fetch(AND(uid=i)))[0]
                    subject = message.subject
                    body = message.text
                    text = body.split("[Variables]")[0].strip()
                    locations = extract_data(body, "Locations")
                    recipiants = extract_data(body, "Recipients")

                    for j in recipiants:
                        data = j.split(": ")
                        recipiant = data[0]
                        location_list = data[1]
                        loc_list = []
                        for i in range(len(locations)):
                            location = locations[i]
                            loc_data = int(location_list[i])
                            if loc_data == 1:
                                loc_list.append(location)
                        recipiant_loc_list[recipiant] = loc_list
                    
                    data={
                        "key": key,
                        "body": text,
                        "subject": subject,
                        "mode": "different",
                        "locs_dict": recipiant_loc_list
                    }
                    resp = requests.post(api, data=json.dumps(data))
                    print(resp.json())
                    
            old_len = len(bodies)
            old_list = bodies
            time.sleep(20)
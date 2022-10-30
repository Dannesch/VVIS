from fastapi import FastAPI
from pydantic import BaseModel

receiver_email = ["dschem.ds@gmail.com"]

# body, subject, receivers = receiver_email, locs:list = ['Karta',"Soderhall","Sattra","Sono","Glugga","Aby","Vaddo","Alunda","Halkriskkarta","Textprognos"]

class Send(BaseModel):
    body: str
    subject: str | None = "VVIS"
    receivers = receiver_email
    locs: list | None = ['Karta',"Soderhall","Sattra","Sono","Glugga","Aby","Vaddo","Alunda","Halkriskkarta","Textprognos"]


app = FastAPI()


@app.post("/send/")
async def create_item(data: Send):
    return data.body

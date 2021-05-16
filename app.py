from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def findStart(data):
  for n in data["nodes"]:
     if n["type"] == "basic/start":
         return n["id"]

def findNode(id,data):
  for n in data["nodes"]:
     if n["id"] == id:
         print("found %d " % ( id ))
         return n

def execute(link,data):
    origin = findNode(link[1],data)
    target = findNode(link[3],data)
    print(origin["type"])
    print(origin["properties"])
    print(target["type"])

def recurcivecross(links, data, id ):
  for n in data["links"]:
       if n[1] == id: 
         execute(n, data)
         recurcivecross(links, data, n[3])
 

@app.get("/listsaved", response_class=HTMLResponse)
async def listfile(request: Request):
    arr = os.listdir("datasaved")
    result =[]
    for a in arr:
        result.append({'text':a,'value':a})

    return json.dumps(result) 

@app.post("/save", response_class=HTMLResponse)
async def save(request: Request):
    payload = await request.json()    
    # TODO check security in string...
    with open(os.path.join('datasaved',"%s.json" % (payload["name"])), "w") as file1:
        file1.write(json.dumps(payload["data"]))    
        return "OK"    

@app.get("/load/{filejson}", response_class=HTMLResponse)
async def load(filejson: str):
    print(filejson)
    with open(os.path.join('datasaved',filejson), "r") as file1:
        return file1.read()

@app.post("/run", response_class=HTMLResponse)
async def run(request:Request):
    payload = await request.json()    
    data = payload["data"]
    startid = findStart(data)
    recurcivecross(data["links"],data,startid)



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "id": id})

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, debug=True,log_level="info")


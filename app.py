from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import uvicorn
import os
import json
import pprint

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def factoryFunction( typenode, nodesource, nodetarget ):
     if typenode == "if/contains":
          if nodesource["result"]["text"].find(nodetarget["properties"]["contains"]) is not -1:
               return True
          else:
               return False
     if typenode == "basic/log":
          print(" basic log ")
          print(nodetarget["properties"]["message"])
          return nodetarget["properties"]["message"]
     return {}

class LiteGraphExecute:
    def __init__(self, data):
        self._data = data
        self._idstart = self.findStart() 
        # Result cache of node , idnode : result
        self._cachedresult = {}

    def findStart(self):
        for n in self._data["nodes"]:
            if n["type"] == "basic/start":
                return n["id"]

    def findNode(self, id):
        for n in self._data["nodes"]:
            if n["id"] == id:
                return n

    def execute(self, link):
        origin = self.findNode(link[1])
        target = self.findNode(link[3])
        print(origin["type"])
        print(origin["properties"])
        print(target["type"])
        for index,n in enumerate(self._data["nodes"]):
            if n["id"] == link[3]:
                if "result" not in n:
                     self._data["nodes"][index]["result"] = factoryFunction(target["type"],origin,target)

                return self._data["nodes"][index]["result"] 


    def recurcivecross(self, links, id ):
        result = ""
        for l in self._data["links"]:
            if l[1] == id: 
                origin = self.findNode(l[1])
                # test node if.
                if origin["type"].find("if/") is not -1:
                      # the way is True slot 0 
                      print(l)
                      pprint.pprint(origin)
                      if l[2] == 0 and origin["result"] is True:
                          tmpresult = json.dumps(self.execute(l))
                          print("WAY TRUE")
                          if tmpresult is not None:
                            result  = result + json.dumps(tmpresult)

                      elif l[2] == 1 and origin["result"] is False:
                          tmpresult = json.dumps(self.execute(l))
                          print("WAY FALSE")
                          if tmpresult is not None:
                            result  = result + json.dumps(tmpresult)
                else:
                      tmpresult = json.dumps(self.execute(l))
                      if tmpresult is not None:
                            result  = result + json.dumps(tmpresult)
                
                tmpresult = self.recurcivecross(links, l[3])
                if tmpresult is not None:
                      result = result + tmpresult
        return result
 
    def run(self):
        return self.recurcivecross(self._data["links"], self._idstart)

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
    
    lge = LiteGraphExecute( payload["data"] )
    return JSONResponse(content=lge.run())



@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "id": id})

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, debug=True,log_level="info")


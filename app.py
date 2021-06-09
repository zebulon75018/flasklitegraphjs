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

import json
import pprint
import plugin as pg

pm = pg.pluginManager("plugins")

data = {}
objid = {}


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class NodeGraph:
    def __init__(self, node, nobj):
       self._node = node
       self._nobj = nobj
       self._input = []
       self._output = []
       self._computed = False

    def addInput(self, input):
       self._input.append(input)

    def addOutput(self, out):
       self._output.append(out)

    def getId(self):
       return self._node["id"] 

    def getType(self):
       return self._node["type"] 
   
    def display(self):
       if len(self._input)!=0:
           for i in self._input:
               print("\t %s " % ( i._node["type"] ))
       if len(self._output)!=0:
           for o in self._output: 
               print("\t %s " % (o._node["type"]))
    
    def isComputed(self):
        return self._computed

    def run(self):
        self._computed = True
        print(" RUN %s \n" % ( self._node["type"] ))
        param=[]
        for i in self._input:
              if i.isComputed() == False:
                     i.run() 
              param.append(i._nobj.getValue(i._node))
        print(param)
        result = self._nobj.execute(param)

        if len(self._output) == 0:
           print("RESULT")
           print(result)
           return result

        for o in self._output:
             return o.run()

class Graph:
    def __init__(self):
      self._listnode = []
      self._result =""

    def addNode(self, node, nobj):
      self._listnode.append(NodeGraph(node,nobj))
   
    def findNode(self, id ):
      for ng in self._listnode:
           if ng.getId() == id:
                 return ng

    def findStart(self):
      for ng in self._listnode:
           if ng.getType() ==  "basic/start":
                 return ng


    def connect(self, idinput, idoutput):
      nginput  = self.findNode(idinput)
      ngoutput = self.findNode(idoutput)
      nginput.addOutput(ngoutput)
      ngoutput.addInput(nginput)

    def display(self ):
      for ng in self._listnode:
         ng.display()
   
    def result(self):
       return self.result


def findclasse( name ) : 
    for obj in pm.classes():
         if name == "basic/%s" % type(obj).__name__:
             #print(" Found %s " %( type(obj).__name__))
             return obj
    return None

def findStart(data):
  for n in data["nodes"]:
     if n["type"] == "basic/start":
         return n["id"]

def findNode(id):
  for n in data["nodes"]:
     if n["id"] == id:
         print("found %d " % ( id ))
         return n

def getinput(node):
   return node["inputs"]

def execute(link):
    origin = findNode(link[1])
    target = findNode(link[3])
    for i in getinput(target):
        n1 = findNode(i["link"])
        n1obj = findclasse(n1["type"])
        print(n1obj.getValue(n1))

    print(origin["type"])
    objorigin = findclasse(origin["type"])
    objtarget = findclasse(target["type"])
    objid[origin["id"]] = findclasse(origin["type"])
    objid[target["id"]] = findclasse(target["type"])
    print(origin["properties"])
    print(target["type"])

def recurcivecross(links, id ):
  for n in data["links"]:
       if n[1] == id: 
         execute(n)
         recurcivecross(links,  n[3])
 


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
        file1.write(json.dumps(payload["data"], indent=4))    
        return "OK"    

@app.get("/load/{filejson}", response_class=HTMLResponse)
async def load(filejson: str):
    print(filejson)
    with open(os.path.join('datasaved',filejson), "r") as file1:
        return file1.read()

@app.post("/run", response_class=JSONResponse)
async def run(request:Request):
    payload = await request.json()    
    g = Graph()
    data = payload["data"]
    for n in data["nodes"]:
      nobj = findclasse(n["type"])
      g.addNode(n,nobj)
    for l in data["links"]:
      g.connect(l[1],l[3])

    #g.display()
    print(g.findStart().run())
    return JSONResponse( g.findStart().run() )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "id": id})

if __name__ == "__main__":
    uvicorn.run("readlitegraph:app", host="127.0.0.1", port=5002, debug=True,log_level="info")

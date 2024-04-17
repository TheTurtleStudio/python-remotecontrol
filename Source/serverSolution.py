import socket
from threading import Thread
from queue import Queue
from queue import Empty
from subprocess import run
from subprocess import TimeoutExpired
from json import loads
from json import load
from time import sleep
from urllib import request
from os import path
from os import remove

#Variables for holding information about connections
connections = []
total_connections = 0

#Threads
taskThread = None
newConnectionsThread = None

#Variables for handling method execution
taskQueue = Queue()
returnQueueDict = {}

class Client(Thread):
  def __init__(self, socket, address, id, signal):
    Thread.__init__(self)
    self.socket = socket
    self.address = address
    self.id = id
    self.signal = signal
    self.socket.settimeout(0.1)
    returnQueueDict[self.socket] = Queue()
    
  def __str__(self):
    return str(self.id) + " " + str(self.address)
    
  def run(self):
    
    while self.signal:
      data = None
      try:
        returnValue = str.encode(str(returnQueueDict[self.socket].get(block=False)))
        self.socket.send(returnValue)
      except Empty:
        pass
      try:
        data = self.socket.recv(4096)
      except socket.timeout:
        pass
      except socket.error:
        print(f"-{self.address}")
        self.signal = False
        connections.remove(self)
        break
      if data != "" and data != None:
        if data.decode == "-1": #REFORMAT TO JSON COMPATIBLE
          pass
          #Instead set event for taskCompleter thread
        try:
          dataJson = loads(data.decode("utf-8").replace("'", '"'))
          dataJson["sourceSocket"] = self.socket
          taskQueue.put(dataJson)
        except Exception as e:
          returnQueueDict[self.socket].put({"stdout": "", "stderr": e})
      
                        

def newConnections(socketConnection):
  while True:
    try:
      sock, address = socketConnection.accept()
    except socket.timeout:
      continue
    global total_connections
    connections.append(Client(sock, address, total_connections, True))
    print(f"+{address}")
    connections[len(connections) - 1].start()
    total_connections += 1

def taskCompleter():
  while True:
    try:
      task = taskQueue.get(block=False)
    except Empty:
      sleep(0.4)
      continue
    try:
      execution = task["execution"]
      executionData = task["executionData"]
    except KeyError as e:
      returnQueueDict[task["sourceSocket"]].put({"stdout": "", "stderr": e})
      continue
    if execution == "UPDATE":
      optionsFile = open('options.json',)
      optionsJson = load(optionsFile)
      optionsFile.close()
      if path.exists("methods.exe"):
        remove("methods.exe")
      request.urlretrieve(optionsJson["server"]["methodsURL"], filename="methods.exe")
      #UPDATE METHODS.PY
    else:
      #In passed in JSON, we run .replace("'", '"') to replace single quotes with double quotes. Fuck JSON lib. Take my single quotes, that's what python automatically gives me for dicts.
      try:
        returnQueueDict[task["sourceSocket"]].put(str({"execution": execution, "executionData": loads(str(executionData))}).replace("'", '"'))
      except Exception as e:
        returnQueueDict[task["sourceSocket"]].put({"stdout": "", "stderr": e})
      try:
        result = run(["methods.exe", str({"execution": execution, "executionData": loads(executionData)}).replace("'", '"')], capture_output=True, text=True)
      except TimeoutExpired:
        continue
      except Exception as e:
        returnQueueDict[task["sourceSocket"]].put({"stdout": "", "stderr": e})
      else:
        returnQueueDict[task["sourceSocket"]].put({"stdout": result.stdout, "stderr": result.stderr})
    
def main():
    host = socket.gethostbyname(socket.gethostname())
    port = 7544
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)

    global newConnectionsThread
    global taskThread
    newConnectionsThread = Thread(target = newConnections, args = (sock,))
    taskThread = Thread(target = taskCompleter)
    newConnectionsThread.start()
    taskThread.start()
    
main()

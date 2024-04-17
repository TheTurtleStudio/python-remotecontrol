import socket
import threading
import sys
import json

#Wait for incoming data from server
#.decode is used to turn the message in bytes to a string
def receive(socket, signal):
    while signal:
        try:
            data = socket.recv(4096)
            print(str(data.decode("utf-8")))
            
        except:
            print("You have been disconnected from the server")
            signal = False
            break

#Get host and port
optionsFile = open("options.json", "r")
optionsJson = json.load(optionsFile)
optionsFile.close()
host = optionsJson["client"]["serverIP"]
port = 7544

#Attempt connection to server
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
except:
    print("Could not make a connection to the server")
    input("Press enter to quit")
    sys.exit(0)

#Create new thread to wait for data
receiveThread = threading.Thread(target = receive, args = (sock, True))
receiveThread.start()

#Send data to server
#str.encode is used to turn the string message into bytes so it can be sent across the network
while True:
    message = input()
    try:
        sock.send(str.encode(message))
        #sock.send(str.encode(str({"execution": "GET", "executionData": "{}"})))
    except ConnectionResetError:
        print("Not connected.")

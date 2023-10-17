# connection = {
#    "id": id (int),
#    "clientId": "clientVCI_SN" (int), or None (if None, status is "pending")
#    "clientSocket": socket,
#    "status": "pending" or "serviced" 
#    "connectedTo": id (int) or None (if None, status is "pending")
# }

import socket
import re
import select
import time
from datetime import datetime
import sys

#------------------------------------------------------------
def createSocket(ip, port):
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sck.bind((ip,int(port)))
    sck.setblocking(False)
    sck.listen(5)
    return sck

#------------------------------------------------------------
def socketList(connections, serverSocket):
    socketList = [serverSocket]
    for c in connections:
        socketList.append(c["clientSocket"])
    return socketList

#------------------------------------------------------------
def main(port):
    print("\n\n------------------------------------------------------------")
    print("Central Server 1.0")
    print("------------------------------------------------------------\n")
    connections = []
    serverSocket = createSocket("0.0.0.0", port)
    keepLooping = True
    connectionId = 1
    t0 = time.time()
    while keepLooping:
        if time.time() - t0 > 1.0:
            t0 = time.time()
            print("{} - Connections: {}".format(datetime.now().strftime("%H:%M:%S"), len(connections)), end="\r")
        try:
            readSockets, _, _ = select.select(socketList(connections,serverSocket), [], [],0)
            for s in readSockets:
                if s == serverSocket:
                    clientSocket, _ = s.accept()
                    connections.append( {"id": connectionId, \
                                        "clientId": None, \
                                        "nickname": None, \
                                        "clientSocket": clientSocket, \
                                        "status": "pending", \
                                        "connectedTo": None} )
                    connectionId += 1
                    clientSocket.setblocking(False)
                    clientSocket.send("Connected to server".encode("utf-8"))
                else:
                    for c in connections:
                        if c["clientSocket"] == s:
                            data = c["clientSocket"].recv(1024)
                            if data:
                                txt = data.decode("utf-8")
                                if c["clientId"] == None:
                                    if txt == "master":
                                        c["clientId"] = txt
                                        c["status"] = "serviced"
                                        s.send("Set to master".encode("utf-8"))
                                    elif re.match(r'^vci [0-9]{12}$', txt):
                                        _, id = txt.split(" ")
                                        c["clientId"] = id
                                        c["status"] = "serviced"
                                        s.send(f"VCI {id} connected".encode("utf-8"))
                                elif c["clientId"] == "master":
                                    if txt == "exit":
                                        c["clientSocket"].close()
                                        connections.remove(c)
                                        print("Master disconnected")
                                    elif txt == "list":
                                        s.send("\nList of clients:".encode("utf-8"))
                                        for c in connections:
                                            if c["connectedTo"] == None:
                                                s.send("\nClient {}: {}".format(c["id"], c["clientId"]).encode("utf-8"))
                                            else:
                                                s.send("\nClient {}: {} (connected to {})".format(c["id"], c["clientId"], c["connectedTo"]).encode("utf-8"))
                                            s.send("\nClient {}: {}".format(c["id"], c["clientId"]).encode("utf-8"))
                                    elif re.match(r'^link [0-9]{12} [0-9]{12}$', txt):
                                        VCIs = txt.split(" ")[1:]
                                        linked = False
                                        for c1 in connections:
                                            if c1["clientId"] == VCIs[0]:
                                                for c2 in connections:
                                                    if c2["clientId"] == VCIs[1]:
                                                        c1["connectedTo"] = c2["id"]
                                                        c2["connectedTo"] = c1["id"]
                                                        linked = True
                                                        break
                                                break
                                        if linked:
                                            s.send("Linked".encode("utf-8"))
                                        else:
                                            s.send("Unknown VCI(s)".encode("utf-8"))
                                    elif re.match(r'unlink [0-9]{12}', txt):
                                        VCI = txt.split(" ")[1]
                                        unlinked = False
                                        for c1 in connections:
                                            if c1["clientId"] == VCI:
                                                for c2 in connections:
                                                    if c2["id"] == c1["connectedTo"]:
                                                        c1["connectedTo"] = None
                                                        c2["connectedTo"] = None
                                                        unlinked = True
                                                        break
                                                break
                                        if unlinked:
                                            s.send("Unlinked".encode("utf-8"))
                                else:
                                    if c["connectedTo"] != None:
                                        for c1 in connections:
                                            if c1["id"] == c["connectedTo"]:
                                                c1["clientSocket"].send(data)
                                                break
                                    print("Received data from client {}: {}".format(c["id"], data))
                            else:
                                c["clientSocket"].close()
                                connections.remove(c)
        except KeyboardInterrupt:
            print('Server shutting down!')
            keepLooping = False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    else:
        print("USAGE: python3 Central.py <port>")


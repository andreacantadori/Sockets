import socket 
import select
import sys
import time

# List of ports
workshopPorts = [40000, 40001, 40002, 40003, 40004, 40005, 40006, 40007, 40008, 40009]
OEToolPorts = [50000, 50001, 50002, 50003, 50004]
controlPort = [45000]
linkedPorts = []

baseSocketIP = '0.0.0.0'

# List of running connections
serverSockets = []
clientSockets = []

#------------------------------------------------------------
def createSocket(ip, port):
    # Create socket
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Set socket options
    sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind to IP and Port
    sck.bind((ip,int(port)))
    # Set the socket to non-blocking
    sck.setblocking(False)
    # Enable the server to accept connections
    sck.listen(1)
    return sck

#------------------------------------------------------------
def createServersListeningOn(ports):
    global baseSocketIP
    serverList = []
    for port in ports:
        s = createSocket(baseSocketIP, port)
        if s is not None:
            serverList.append(s)
            print(f"[*] Socket on port {port}")
        else:
            print(f"ERROR: Could not create socket on port {port}")
    return serverList

#------------------------------------------------------------
def main():

    global serverSockets
    global linkedPorts

    serverSockets += createServersListeningOn(OEToolPorts)
    serverSockets += createServersListeningOn(workshopPorts)
    serverSockets += createServersListeningOn(controlPort)

    socketsList = []
    for s in serverSockets:
        socketsList.append(s)
    loop = True

    while loop:
        try:
            readSockets, _, _ = select.select(socketsList, [], socketsList, 0)
            for s in readSockets:
                if s in serverSockets:
                    clientSocket, clientAddress= s.accept()
                    print(f"New connection from {clientAddress}")
                    socketsList.append(clientSocket)
                    clientSockets.append(clientSocket)
                elif s in clientSockets:
                    _, port = s.getsockname()
                    try:
                        if port == controlPort[0]:
                            try:
                                message = s.recv(1024).decode('utf-8')
                                try:
                                    cmd, A, B = message.split(" ")
                                    portA = int(A)
                                    portB = int(B)
                                except ValueError:
                                    cmd = message
                                    portA = -1
                                    portB = -1
                                print(f"Requested action: {message} ")
                                if cmd == 'bind' and portA != portB and portA>0 and portB>0:
                                    portAisInUse = any(portA in linkedPair for linkedPair in linkedPorts)
                                    portBisInUse = any(portB in linkedPair for linkedPair in linkedPorts)
                                    if portAisInUse or portBisInUse:
                                        print(f"ERROR: One or both ports are already in use")
                                        s.send("ERROR: One or both ports are already in use".encode('utf-8'))
                                    else:
                                        s.send("OK".encode('utf-8'))
                                        linkedPorts.append([portA, portB])
                                elif cmd == 'unbind' and portA != portB and portA>0 and portB>0:
                                    portAB = any([portA, portB] in linkedPorts)
                                    portBA = any([portB, portA] in linkedPorts)
                                    if portAB is not None:
                                        s.send("OK".encode('utf-8'))
                                        linkedPorts.remove([portA, portB])
                                    elif portBA is not None:
                                        s.send("OK".encode('utf-8'))
                                        linkedPorts.remove([portB, portA])
                                    else:
                                        print(f"ERROR: One or both ports are not linked")
                                        s.send("ERROR: One or both ports are not linked".encode('utf-8'))
                                elif cmd == 'list':
                                    s.send("\n-----------------------------------".encode('utf-8'))
                                    s.send(f"\nPORT LIST".encode('utf-8'))
                                    for sck in socketsList:
                                        _, port = sck.getsockname()
                                        if port < 50000:
                                            portUsed = False
                                            for c in clientSockets:
                                                if c.getsockname()[1] == port:
                                                    portUsed = True
                                                    break
                                            if portUsed:
                                                s.send(f"\nPort {port}: Workshop, in use".encode('utf-8'))
                                            else:
                                                s.send(f"\nPort {port}: Workshop, available".encode('utf-8'))
                                        else:
                                            portUsed = False
                                            for c in clientSockets:
                                                if c.getsockname()[1] == port:
                                                    portUsed = True
                                                    break
                                            if portUsed:
                                                s.send(f"\nPort {port}: OETool, in use".encode('utf-8'))
                                            else:
                                                s.send(f"\nPort {port}: OETool, available".encode('utf-8'))
                                    if len(linkedPorts) > 0:
                                        s.send(f"\nLinked ports:".encode('utf-8'))
                                        for linkedPair in linkedPorts:
                                            s.send(f"\n    {linkedPair[0]} <-> {linkedPair[1]}".encode('utf-8'))
                                    else:
                                        s.send(f"\nNo linked ports".encode('utf-8'))  
                                else:
                                    s.send(f"\nERROR: Unknown command {cmd}".encode('utf-8'))
                            except ValueError:
                                s.send("\nERROR: Invalid command".encode('utf-8'))
                        else:
                            isLinkedPort = any(port in linkedPair for linkedPair in linkedPorts)
                            if isLinkedPort:
                                for linkedPair in linkedPorts:
                                    if port in linkedPair:
                                        if port == linkedPair[0]:
                                            linkedPort = linkedPair[1]
                                        else:
                                            linkedPort = linkedPair[0]
                                        break
                                linkedSocket = [ls for ls in clientSockets if ls.getsockname()[1] == linkedPort][0]
                                message = s.recv(1024).decode('utf-8')
                                print(f"Message {message} from {port}")
                                linkedSocket.send(message.encode('utf-8'))
                                print(f"    Echoed to {linkedPort}")
                            else:
                                pass
                                #print("WARNING: Port is not linked, message has no effect")
                    except socket.error as e:
                        pass
        except KeyboardInterrupt:
            print('Server shutting down!')
            loop = False



if __name__ == "__main__":
    main()

import socket 
import PortServices as ps
import MRD_constants as const
import select

#------------------------------------------------------------
def createSocket(ip, port):
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sck.bind((ip,int(port)))
    sck.setblocking(False)
    sck.listen(1)   # Socket will only allow for 1 connection at a time
    return sck

#------------------------------------------------------------
def createServersListeningOn(ports, baseSocketIP):
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
def isServerConnectedToAnyClient(s, listOfClientSockets):
    for c in listOfClientSockets:
        if c.getsockname()[1] == s.getsockname()[1]:
            return True
    return False

#------------------------------------------------------------
def checkAndRemoveClosedConnections(clientSockets):
    closedConnections = []
    for c in clientSockets:
        try:
            c.send("".encode('utf-8'))
        except socket.error as e:
            closedConnections.append(s)
    return closedConnections

#------------------------------------------------------------
def serveClientSocket(c, clientSockets, serverSockets, linkedPorts):
    port = ps.portForSocket(c)
    try:
        if port == const.CONTROL_PORT:
            serveControlSocket(c, clientSockets, serverSockets, linkedPorts)
        else:   
            ps.portForwarding(c, clientSockets, linkedPorts)
    except socket.error as e:
        print(f"ERROR <serverClientSocket>: {str(e)}")

#------------------------------------------------------------
def serveControlSocket(s, clientSockets, serverSockets, linkedPorts):                                 
    try:    
        cmd = s.recv(1024).decode('utf-8')
        try:
            nParametersInCommand = cmd.count(" ")
            if nParametersInCommand == 0:
                if cmd == 'list':
                    ps.listPorts(linkedPorts, serverSockets, clientSockets, s)
                elif cmd == 'exit':
                    s.send("OK".encode('utf-8'))
                    s.close()
                    clientSockets.remove(s)
                    unbindPort(portForSocket(s), linkedPorts)
                else:
                    s.send(f"\nERROR: Unknown command {cmd}".encode('utf-8'))
            elif nParametersInCommand == 1:
                cmd, A = cmd.split(" ")
                if cmd == 'unbind':
                    try:
                        portA = int(A)
                        if ps.unbindPort(portA, linkedPorts):
                            s.send(f"Port {A} unbound".encode('utf-8'))
                        else:
                            s.send("ERROR: One or both ports are invalid ornot linked".encode('utf-8'))
                    except ValueError:
                        s.send("ERROR: Invalid port number".encode('utf-8'))
                else:
                    s.send(f"\nERROR: Unknown command {cmd}".encode('utf-8'))
            elif nParametersInCommand == 2:
                cmd, A, B = cmd.split(" ")
                if cmd == 'bind':
                    try:
                        portA = int(A)
                        portB = int(B)
                        if ps.bindPorts(portA, portB, linkedPorts, clientSockets):
                            s.send("OK".encode('utf-8'))
                        else:
                            s.send("ERROR: One or both ports are invalid already in use".encode('utf-8'))
                    except ValueError:
                        s.send("ERROR: Invalid port number".encode('utf-8'))
                else:
                    s.send(f"\nERROR: Unknown command {cmd}".encode('utf-8'))
            else:
                s.send("\nERROR: Too many parameters".encode('utf-8'))      
        except ValueError:
            s.send("\nERROR: Rx error".encode('utf-8'))      
    except ValueError:
        s.send("\nERROR: Rx error".encode('utf-8'))

#-----------------------------------------------------------
def socketsReadyForReading(socketsList):
    try:
        for s in socketsList:
            if s.fileno() == -1:
                socketsList.remove(s)
        readSockets, _, _ = select.select(socketsList, [], socketsList, 0)
        return readSockets
    except ValueError as e:
        print(f"ERROR <socketReadyForReading>: {str(e)}")
        return []


import socket
import select
import sys

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
    sck.listen(5)
    print(f'Socket waiting on {ip}:{port}')
    return sck

socketList = []

#------------------------------------------------------------
def bindPorts(s):
    message = s.recv(1024)
    if message:
        action, portA, portB = message.decode('utf-8').split(" ")
        print(f"Requested action: {message} ")
        if action == 'bind':
            print(f"Binding ports {portA} and {portB}")
            serverSocketA = createSocket('', int(portA))
            serverSocketB = createSocket('', int(portB))
            socketList.append(serverSocketA)
            socketList.append(serverSocketB)

#------------------------------------------------------------
def acceptConnection(serverSocket):
    global socketList
    clientSocket, clientAddress = serverSocket.accept()
    print(f"New connection from {clientAddress}")
    socketList.append(clientSocket)
    return clientSocket

#------------------------------------------------------------        
def echoMessage(fromSocket, toSocket):
    message = fromSocket.recv(1024)
    if message:
        print(f"Message {message} from {fromSocket.getpeername()}")
        if toSocket is not None:
            toSocket.send(message)
            print(f"    Echoed to {toSocket.getpeername()}")
        else:
            print("ERROR: Destination socket is not available")
    else:
        print(f"Connection closed from {fromSocket.getpeername()}")
        socketList.remove(fromSocket)

#------------------------------------------------------------
def process(port0, portA, portB):

    global socketList

    serverSocket0 = createSocket('', port0)
    serverSocketA = createSocket('', portA)    
    serverSocketB = createSocket('', portB)
    socketList = [serverSocket0, serverSocketA, serverSocketB]

    try:
        clientSocket0 = None
        clientSocketA = None
        clientSocketB = None
        while True:            
            try:
                # Use select to wait for a specific change (read availability) on a socket
                readSockets, _, _ = select.select(socketList, [], socketList)

                for notifiedSocket in readSockets:

                    if notifiedSocket == serverSocket0:
                        clientSocket0 = acceptConnection( notifiedSocket)
                    elif notifiedSocket == serverSocketA:
                        clientSocketA = acceptConnection( notifiedSocket)
                    elif notifiedSocket == serverSocketB:
                        clientSocketB = acceptConnection( notifiedSocket)
                    elif notifiedSocket == clientSocket0:
                        bindPorts(notifiedSocket)        
                    elif notifiedSocket == clientSocketA:
                        echoMessage(clientSocketA, clientSocketB)
                    elif notifiedSocket == clientSocketB:
                        echoMessage(clientSocketB, clientSocketA)
                            
            except Exception as e:
                print(f'Error occurred: {str(e)}')

    except KeyboardInterrupt:
        print('Server shutting down!')

if __name__ == "__main__":
    process(45000, 50001, 40001)
    if len(sys.argv) > 3:
        process(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    else:
        print ("Usage: python3 portForwarding.py <controlPort> <portA> <portB>")

import PBX_Constants as const
import select
import socket

#------------------------------------------------------------
def bindPorts(A, B, linkedPorts, clientSockets):
    if A != B and A > 0 and B > 0:
        if any(A in linkedPair for linkedPair in linkedPorts) or any(B in linkedPair for linkedPair in linkedPorts):
            return False
        else:
            if len(clientSockets) < 2:
                return False
            elif [ls for ls in clientSockets if ls.getsockname()[1] == A] is not None \
                and [ls for ls in clientSockets if ls.getsockname()[1] == B] is not None:                            
                linkedPorts.append([A, B])
                return True
            else:
                return False
    else:
        return False

#------------------------------------------------------------
def unbindPort(port, linkedPorts):
    pair = None
    for linkedPair in linkedPorts:
        if int(port) in linkedPair:
            pair = linkedPair
            break
    if pair is not None:
        linkedPorts.remove(pair)
        return True
    return False

#------------------------------------------------------------
def portForwarding(s, clientSockets, linkedPorts):
    try:
        message = s.recv(4096,0)
        if not message:
            unbindPort(portForSocket(s), linkedPorts)
            s.close()
            clientSockets.remove(s)
        else:
            for linkedPair in linkedPorts:
                port = portForSocket(s)
                if port in linkedPair:
                    if port == linkedPair[0]:
                        linkedPort = linkedPair[1]
                    else:
                        linkedPort = linkedPair[0]
                    # Get the socket that is linked to the one that received the message
                    linkedSocket = [ls for ls in clientSockets if ls.getsockname()[1] == linkedPort] 
                    # Note that linkedSocket is a list of sockets, but there should only be one
                    # We check that the list is not empty before sending the message to the linked socket
                    # (this may happen if the linked socket has been closed)
                    # Send the message to the linked socket
                    if len(linkedSocket) > 0:                            
                        linkedSocket[0].send(message)
                    else:
                        ps.unbindPort(portForSocket(s), linkedPorts)
                        s.close()
                        clientSockets.remove(s)
                    break
    except ValueError:
        s.send("\nERROR: Rx error".encode('utf-8'))

#------------------------------------------------------------
def portForSocket(s):
    try:
        port = s.getsockname()[1]
    except ValueError:
        port = -1
    return port

#------------------------------------------------------------
def listPorts(linkedPorts, serverSockets, clientSockets, currentSocket):
    currentSocket.send("\n-----------------------------------".encode('utf-8'))
    currentSocket.send("\nPORT LIST".encode('utf-8'))
    for sck in serverSockets:
        _, port = sck.getsockname()
        if port != const.CONTROL_PORT:
            if port < 50000:
                portUsed = False
                for c in clientSockets:
                    if c.getsockname()[1] == port:
                        portUsed = True
                        break
                if portUsed:
                    currentSocket.send(f"\nPort {port}: Workshop  in use".encode('utf-8'))
                else:
                    currentSocket.send(f"\nPort {port}: Workshop  available".encode('utf-8'))
            else:
                portUsed = False
                for c in clientSockets:
                    if c.getsockname()[1] == port:
                        portUsed = True
                        break
                if portUsed:
                    currentSocket.send(f"\nPort {port}: OETool    in use".encode('utf-8'))
                else:
                    currentSocket.send(f"\nPort {port}: OETool    available".encode('utf-8'))
    if len(linkedPorts) > 0:
        currentSocket.send(f"\nLinked ports:".encode('utf-8'))
        for linkedPair in linkedPorts:
            currentSocket.send(f"\n    {linkedPair[0]} <-> {linkedPair[1]}".encode('utf-8'))
    else:
        currentSocket.send(f"\nNo linked ports".encode('utf-8'))
                                    


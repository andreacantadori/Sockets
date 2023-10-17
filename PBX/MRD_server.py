import socket 
import select
import SocketServices as ss
import PortServices as ps
import MRD_constants as const

# Base ports are only used to get the port numbers for the OETool and Workshop
# The port numbers are stored in lists
workshopPorts = [const.BASE_WORKSHOP_PORT + i for i in range(const.N_PORTS)]
OEToolPorts = [const.BASE_OETOOL_PORT + i for i in range(const.N_PORTS)]


#------------------------------------------------------------
def main():

    # Create list of server sockets
    serverSockets  = ss.createServersListeningOn(OEToolPorts, const.BASE_SOCKET_IP)
    serverSockets += ss.createServersListeningOn(workshopPorts, const.BASE_SOCKET_IP)
    serverSockets += ss.createServersListeningOn([const.CONTROL_PORT], const.BASE_SOCKET_IP)

    # Mutable list of sockets to monitor for I/O (server and client sockets)
    # CLient sockets are added to this list when they connect
    socketsList = [s for s in serverSockets]

    # Mutable list of linked ports - empty at the beginning
    linkedPorts = []

    # Mutable list of client sockets - empty at the beginning
    clientSockets = []

    keepLooping = True
    while keepLooping:
        try:
            # In each loop we constantly chck for closed connections
            # and remove them from the list of sockets to monitor
            # We also unbind any ports that are no longer in use
            for c in ss.checkAndRemoveClosedConnections(clientSockets):
                socketsList.remove(s)
                clientSockets.remove(s)
                ps.unbindPort(portForSocket(c), linkedPorts)
            # Check for sockets ready for reading, i.e. sockets that have received data
            for s in ss.socketsReadyForReading(socketsList):
                # First serve client sockets, then server sockets
                if s in clientSockets:
                    ss.serveClientSocket(s, clientSockets, serverSockets, linkedPorts)
                elif s in serverSockets:
                    # If the server socket is not connected to any client, we accept the connection
                    # and add the client socket to the list of sockets to monitor
                    # Otherwise, we just ignore the request and let it time out
                    if not ss.isServerConnectedToAnyClient(s, clientSockets):
                        clientSocket, _ = s.accept()
                        socketsList.append(clientSocket)
                        clientSockets.append(clientSocket)
        except KeyboardInterrupt:
            print('Server shutting down!')
            keepLooping = False



if __name__ == "__main__":
    main()

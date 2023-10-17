import socket
import sys
import keyboard
import select


def is_alphanumeric(key):
    return len(key) == 1 and key.isalnum()

#------------------------------------------------------------
def start_client(ip, port):


    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setblocking(True)
    
    connected = False
    try:
        client_socket.connect((ip, port))
        client_socket.setblocking(False)
        connected = True
        print(f"[*] Connected to {ip}:{port}")
    except socket.timeout as e:
        print(f"[*] Timeout: {str(e)}")
    except socket.error as e:
        print(f"[*] Error: {str(e)}")

    if connected:
        keepLooping = True
        txStr = ""
        try:
            while keepLooping:
                readSockets, writeSockets, _ = select.select([client_socket], [client_socket], [], 0)
                for s in readSockets:
                    data = s.recv(1024)
                    if data:    
                        txt = data.decode("utf-8")
                        if txt == "exit":
                            keepLooping = False
                        else:
                            print(f"Received: {txt}")
                            s.send(f"Received: {txt}. Thank you!".encode("utf-8"))
                for s in writeSockets:
                    try:
                        kbdEvent = keyboard.read_event(suppress=True)
                        if kbdEvent.event_type == keyboard.KEY_DOWN and kbdEvent.event_type != keyboard.KEY_UP:
                            if kbdEvent.name == "enter":
                                print(f"Sending: {txStr}")
                                s.send(txStr.encode("utf-8"))
                                txStr = ""
                            elif is_alphanumeric(kbdEvent.name):
                                txStr += kbdEvent.name
                            elif kbdEvent.name == "space":
                                txStr += " "
                    except KeyboardInterrupt:
                        keepLooping = False

        except socket.timeout as e:
            print(f"[*] Timeout: {str(e)}")
        except socket.error as e:
            print(f"[*] Error: {str(e)}")
        client_socket.close()


# Example usage:
# Connect to a server at IP 127.0.0.1 on port 8888
if __name__ == "__main__":
    #start_client('ec2-54-156-68-18.compute-1.amazonaws.com', 45000)
    #start_client('127.0.0.1', 40001, 'remote')

    if True:
        if len(sys.argv) > 2:
            start_client(sys.argv[1], int(sys.argv[2]))
        else:
            print("USAGE: python3 Client.py <IP> <port>")


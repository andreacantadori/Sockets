import socket
import sys
import time
import random
import select

def randomBinaryString():
    return ''.join([hex(random.randint(0,255))+' ' for i in range(random.randint(1,8))])

#------------------------------------------------------------
def start_client(ip, port, type):


    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(5.0)
    client_socket.setblocking(False)
    
    connected = False
    try:
        client_socket.connect((ip, port))
    except socket.timeout as e:
        print(f"[*] Timeout: {str(e)}")
    except socket.error as e:
        if e.errno == socket.errno.EINPROGRESS:
            # Connection is in progress, use select to wait for it to complete
            _, writable, _ = select.select([], [client_socket], [], 5.0)
            if client_socket in writable:
                print(f"[*] Connected to {ip}:{port}")
                connected = True
            else:
                print("Connection failed")
        else:
            print(f"[*] Error: {str(e)}")

    if connected:
        t0 = time.time()
        dT = random.random() * 5.0
        keepLooping = True
        try:
            while keepLooping:
                if type == 'control':
                    cmd = input("Enter command: ")
                    if cmd == 'exit':
                        keepLooping = False
                    else:
                        client_socket.send(cmd.encode('utf-8'))
                        print("Wait...")
                        time.sleep(2.0)
                        try:
                            print(client_socket.recv(4096).decode('utf-8'))
                        except socket.error as e:
                            pass    
                else:
                    try:
                        rxTime = int(time.time() * 1000)
                        data = client_socket.recv(1024,0)
                        s = data.decode('utf-8')
                        try:
                            t, s = s.split(':')
                            deltaTime = rxTime - int(t)
                            print(f"<-- Ping {deltaTime}, {s}")
                        except ValueError:
                            pass
                    except socket.error as e:
                        pass
                    if time.time() - t0 > dT:
                        t0 = time.time()
                        dT = random.random() * 5.0
                        r = randomBinaryString()
                        t = str(int(time.time() * 1000))
                        s = (t + ':' + r).encode('utf-8')
                        client_socket.send(s)
                        print(f"--> {s}")
        except socket.timeout as e:
            print(f"[*] Timeout: {str(e)}")
        except socket.error as e:
            if e.errno == socket.errno.EINPROGRESS:
                # Connection is in progress, use select to wait for it to complete
                readable, writable, _ = select.select([], [client_socket], [], 5.0)
                if client_socket in writable:
                    # Connection successful
                    print("Connected")
                else:
                    # Connection failed
                    print("Connection failed")
            else:
                print(f"[*] Error: {str(e)}")
        client_socket.close()


# Example usage:
# Connect to a server at IP 127.0.0.1 on port 8888
if __name__ == "__main__":
    #start_client('ec2-54-156-68-18.compute-1.amazonaws.com', 45000)
    #start_client('127.0.0.1', 40001, 'remote')

    if True:
        if len(sys.argv) > 3:
            start_client(sys.argv[1], int(sys.argv[2]), sys.argv[3])
        else:
            print("USAGE: python3 Client.py <IP> <port> <control|remote>")


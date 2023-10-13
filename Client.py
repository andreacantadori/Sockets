import socket
import sys
import time
import random

def start_client(ip, port, type):

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the server at the specified IP and port
        client_socket.connect((ip, port))
        print(f"[*] Connected to {ip}:{port}")
        # Set the socket to non-blocking
        client_socket.setblocking(False)

        i = random.randint(0, 10000)
        while True:
            if type == 'control':
                cmd = input("Enter command: ")
                if cmd == 'exit':
                    break
                else:
                    client_socket.send(cmd.encode('utf-8'))
                    try:
                        print(client_socket.recv(4096).decode('utf-8'))
                    except socket.error as e:
                        pass    
            else:
                try:
                    data = client_socket.recv(1024)
                    print(f"        RX {data}")
                except socket.error as e:
                    pass    
                client_socket.send(str(i).encode('utf-8'))
                print(f"TX {i}")
                time.sleep(1.0)
                i += 1
    except socket.error as e:
        print(f"[*] Error: {str(e)}")
    finally:
        # Close the socket
        client_socket.close()
        print("[*] Connection closed.")



# Example usage:
# Connect to a server at IP 127.0.0.1 on port 8888
if __name__ == "__main__":
    #start_client('ec2-54-156-68-18.compute-1.amazonaws.com', 45000)
    #start_client('127.0.0.1', 40001, 'remote')

    if True:
        if len(sys.argv) > 3:
            start_client(sys.argv[1], int(sys.argv[2]), sys.argv[3])
        else:
            print("USAGE: python3 Client.py <IP> <control|remote>")
    while True:
        pass


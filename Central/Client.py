import threading
import socket
import sys
import select

user_input = ""
lock = threading.Lock()

def client_thread(ip, port):
    global user_input
    # Create a socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setblocking(True)
    # Connect to the server
    server_address = (ip, port) 
    client_socket.connect(server_address)

    keepLooping = True
    while keepLooping:
        readable, _, _ = select.select([client_socket], [], [],0)
        if client_socket in readable:
            data = client_socket.recv(1024)
            if data:
                print(data.decode("utf-8"))
                if data.decode("utf-8") == "exit":
                    keepLooping = False
            else:
                keepLooping = False
        with lock:
            if user_input != "":
                client_socket.send(user_input.encode("utf-8"))
                user_input = ""
    client_socket.close()



if __name__ == "__main__":
    #start_client('ec2-54-156-68-18.compute-1.amazonaws.com', 45000)
    #start_client('127.0.0.1', 40001, 'remote')
    if True:
        if len(sys.argv) > 2:
            # Create a thread for the client
            client_thread = threading.Thread(target=client_thread, args=(sys.argv[1], int(sys.argv[2])))
            #client_thread = threading.Thread(target=client_thread, args=("ec2-54-156-68-18.compute-1.amazonaws.com", 45000))
            # Start the thread
            client_thread.start()
            # Continue with the main program (this can run concurrently with the client thread)
            while True:
                user_input = input(">> ")
                if user_input == 'quit':
                    break
            # Wait for the client thread to finish (optional)
            client_thread.join()
        else:
            print("USAGE: python3 Client.py <IP> <port>")
        print("Main program exited.")

import socket
import select
import sys

BASE_SOCKET_IP = '0.0.0.0'

WORKSHOP_PORTS = [40000, 40001, 40002, 40003, 40004, 40005, 40006, 40007, 40008, 40009]
OETOOL_PORTS = [50000, 50001, 50002, 50003, 50004]
CONTROL_PORT = 45000
linked_ports = []

server_sockets = []
client_sockets = []


def create_server_socket(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, port))
    s.setblocking(False)
    s.listen(1)
    return s


def initialize_server_sockets(ports):
    return [create_server_socket(BASE_SOCKET_IP, port) for port in ports]


def handle_control_port_message(s, message):
    try:
        cmd, A, B = message.split(" ")
        port_a = int(A)
        port_b = int(B)
    except ValueError:
        cmd = message
        port_a = port_b = -1

    if cmd == 'bind' and port_a != port_b and port_a > 0 and port_b > 0:
        port_a_in_use = any(port_a in pair for pair in linked_ports)
        port_b_in_use = any(port_b in pair for pair in linked_ports)
        if port_a_in_use or port_b_in_use:
            s.send("ERROR: One or both ports are already in use".encode('utf-8'))
        else:
            linked_ports.append((port_a, port_b))
            s.send("OK".encode('utf-8'))

    # ... (other command handlers)
    else:
        s.send(f"ERROR: Unknown command {cmd}".encode('utf-8'))


def main():
    global server_sockets, client_sockets

    server_sockets = initialize_server_sockets(OETOOL_PORTS + WORKSHOP_PORTS + [CONTROL_PORT])
    sockets_list = server_sockets.copy()

    while True:
        try:
            read_sockets, _, _ = select.select(sockets_list, [], sockets_list, 0)

            for s in read_sockets:
                if s in server_sockets:
                    client_sock, _ = s.accept()
                    sockets_list.append(client_sock)
                    client_sockets.append(client_sock)
                else:
                    _, port = s.getsockname()
                    if port == CONTROL_PORT:
                        message = s.recv(1024).decode('utf-8')
                        handle_control_port_message(s, message)
                    else:
                        pass
                        # ... (other port handlers)

        except KeyboardInterrupt:
            print('Server shutting down!')
            break


if __name__ == "__main__":
    main()

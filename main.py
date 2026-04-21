import socket
import threading

HOST = "127.0.0.1"
PORT = 9000

clients = []

def broadcast(current_client, msg_type, msg : bytes):
    data = msg_type + len(msg).to_bytes(8, "big") + msg

    for client in clients:
        if client != current_client:
            try:
                client.sendall(data)
            except:
                clients.remove(client)


def recv_data(client, size) -> bytes:
    data = b""
    while len(data) < size:
        pack = client.recv(size - len(data))
        if pack is None:
            break
        data += pack
    return data


def  handle_client(client):
    while True:
        try:
            msg_type = recv_data(client, 1)
            if msg_type is None: break

            msg_size = recv_data(client, 8)
            if msg_size is None: break

            size : int = int.from_bytes(msg_size, "big")
            msg : bytes = recv_data(client, size)

            broadcast(client, msg_type, msg)
        except:
            clients.remove(client)
            client.close()
            break


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        print("Starting server...")
        soc.bind((HOST, PORT))
        soc.listen()
        while True:
            client, addr = soc.accept()
            clients.append(client)
            thread = threading.Thread(target=handle_client, args=(client,))
            thread.start() 
            print(f"Client {addr} connected...") 


if __name__ == "__main__":
    start_server()

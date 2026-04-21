import socket
import threading

HOST = "127.0.0.1"
PORT = 9000


def receive_data(soc, size):
    data = b""
    while len(data) < size:
        pack = soc.recv(size-len(data))
        if (not pack):
            return None
        data += pack
    return data


def receive_msg(soc):
    while True:
        try:
            msg_type : bytes | None = receive_data(soc, 1)
            if (msg_type is None):
                break
            msg_size : bytes | None= receive_data(soc, 8)
            if (msg_size is None):
                break
            size = int.from_bytes(msg_size, "big")
            
            msg : bytes | None = receive_data(soc, size)

            if (msg is None):
                break
            
            if (msg_type == b"T"):
                print('\n'+msg.decode("utf-8")+'\n')
            if (msg_type == b"I"):
                with open("new_file_image.jpg", "wb") as file:
                    file.write(msg)

        except Exception as e:
            print("an error ", e)
            soc.close()
            break


def send_img(soc, img_path : str):
    img_data = b""
    try:
        with open(img_path, "rb") as file:
            img_data = file.read()
        soc.sendall(b"I" + len(img_data).to_bytes(8, "big") + img_data)
    except Exception as e:
        print("ERROR ", e)


def send_msg(soc):
    while True:
        print()
        msg = str(input("> "))
        if not msg: continue
        if (msg.split()[0] == "/image"):
            send_img(soc, msg.split()[1])
        else:
            msg_encoded : bytes = msg.encode("utf-8")
            soc.sendall(b"T" + len(msg_encoded).to_bytes(8, "big") + msg_encoded)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
    soc.connect((HOST, PORT))

    receive_thread = threading.Thread(target=receive_msg, args=(soc,), daemon=True)
    receive_thread.start()

    send_thread = threading.Thread(target=send_msg, args=(soc,), daemon=True)
    send_thread.start()

    receive_thread.join()

import socket
import threading
import json
from pathlib import Path

HOST = "127.0.0.1"
PORT = 9000


class Team:
    id_team : int
    client : socket.socket
    name : str
    password : str


team = Team()


def receive_data(soc, size):
    data = b""
    while len(data) < size:
        pack = soc.recv(size-len(data))
        if (not pack):
            return None
        data += pack
    return data


def chatting_receive(soc):
    while True:
        try:
            msg_type : bytes | None = receive_data(soc, 1)
            if msg_type is None:break
            msg_sender : bytes | None = receive_data(soc, 1)
            if msg_sender is None: break
            msg_sender_id : int = int.from_bytes(msg_sender, "big")
            msg_size : bytes | None= receive_data(soc, 8)
            if msg_size is None:break
            size = int.from_bytes(msg_size, "big")
            
            msg : bytes | None = receive_data(soc, size)
            if (msg is None):break

            if (msg_type == b"T"):
                print('\n'+msg.decode("utf-8")+'\n')
                data = {"sender": msg_sender_id, "receiver": team.id_team, "content":{"text":msg.decode("utf-8")}}
                path = Path(f"chats/{team.id_team}_{msg_sender_id}.json")
                path.write_text(json.dumps(data)+",\n")
                continue
            extension = ""
            match msg_type:
                case b"I": extension = ".jpg"
                case b"P": extension = ".pdf"
            path_images = Path("images")
            file_number = len(list(path_images.glob(extension)))
            file_name = f"images/chat_file_{file_number+1}{extension}"
            file = Path(file_name)
            file.write_bytes(msg)
            data = {"sender": msg_sender_id, "receiver": team.id_team, "content":{extension: file_name}}
            Path(f"chats/{team.id_team}_{msg_sender_id}.json").write_text(json.dumps(data) + ",\n")
        except Exception as e:
            print("an error ", e)
            soc.close()
            break


def send_img(soc, img_path : str, id_receiver):
    img_data = b""
    try:
        with open(img_path, "rb") as file:
            img_data = file.read()
        soc.sendall(b"I" + id_receiver.to_bytes(1, "big") + len(img_data).to_bytes(8, "big") + img_data)
    except Exception as e:
        print("ERROR ", e)


def send_msg(soc, msg, id_receiver):
    msg_encoded : bytes = msg.encode("utf-8")
    soc.sendall(b"T" + id_receiver.to_bytes(1, "big") + len(msg_encoded).to_bytes(8, "big") + msg_encoded)


def chatting_send(soc):
    while True:
        print()
        msg = str(input("> "))
        if not msg or msg[0]!="/": continue
        id_receiver : int = int(msg.split()[0][1:]) 
        msg = msg.strip(msg.split()[0]).strip()
        with open(f"{team.id_team}_{id_receiver}.json", "a") as file:
            if (msg.split()[0] == "/image"):
                img_path = msg.split()[1]
                send_img(soc, img_path, id_receiver)
                data = {"sender": team.id_team, "receiver": id_receiver, "content":{"image": img_path}}
                file.write(json.dumps(data) + ",\n")
            else:
                send_msg(soc, msg, id_receiver)
                data = {"sender": team.id_team, "receiver": id_receiver, "content":{"text": msg}}
                file.write(json.dumps(data) + ",\n")


def start_team(soc) -> Team:
    while True:
        team.name = input("Nome do time > ")
        team.password = input("password > ")
        name_size_bytes = len(team.name).to_bytes(8, byteorder='big')
        password_size_bytes = len(team.password).to_bytes(8, byteorder='big')
        team.client = soc
    
        soc.sendall(
            name_size_bytes + 
            team.name.encode("utf-8") +
            password_size_bytes + 
            team.password.encode("utf-8")
        )
        team_exits : bytes | None = receive_data(soc, 1)
        if team_exits == b"T":
            break
        print("Este usuário não existe...")
    id_team_bytes : bytes | None = receive_data(soc, 1)

    team.id_team = int.from_bytes(id_team_bytes, 'big') if id_team_bytes is not None else -1
    return team


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
    soc.connect((HOST, PORT))

    team = start_team(soc)

    print(f"Você é {team.name} id: {team.id_team}")

    receive_thread = threading.Thread(target=chatting_receive, args=(soc,), daemon=True)
    receive_thread.start()

    send_thread = threading.Thread(target=chatting_send, args=(soc,), daemon=True)
    send_thread.start()

    receive_thread.join()

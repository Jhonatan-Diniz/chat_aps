import socket
import threading
import sqlite3

HOST = "127.0.0.1"
PORT = 9000


class Team:
    id_team : int
    client : socket.socket
    name : str
    password : str

    def is_equal(self, team):
        return 1 if team.name == self.name and team.password == self.password else 0


teams = []
teams_lock = threading.Lock()


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        print("Starting server...")
        soc.bind((HOST, PORT))
        soc.listen()
        while True:
            client, addr = soc.accept()
            print(f"Client {addr} connected...")

            threading.Thread(
                target=client_session,
                args=(client,),
                daemon=True
            ).start()


def client_session(client):
    conn = sqlite3.connect("equipes.db")
    cur = conn.cursor()
    team = None

    try:
        team = login_team(client, cur)
        if team is None: return
        with teams_lock:
            teams.append(team)
        client.sendall(b"T"+team.id_team.to_bytes(1, "big"))
        handle_teams(team)

    finally:
        if team is not None: 
            with teams_lock:
                if team in teams:
                    teams.remove(team)
        client.close()
        conn.close()


def login_team(client, cur) -> Team | None:
    while True:
        name_size_bytes : bytes | None = recv_data(client, 8)
        if name_size_bytes is None: return None
        name_size_int = int.from_bytes(name_size_bytes, "big") 
        name : bytes | None = recv_data(client, name_size_int)
        if name is None: return
    
        password_size_bytes : bytes | None = recv_data(client, 8)
        if password_size_bytes is None: break
        passord_size_int = int.from_bytes(password_size_bytes, "big")
        password : bytes | None = recv_data(client, passord_size_int)
        if password is None: return
    
        team = Team()
        team.name = name.decode('utf-8')
        team.password = password.decode('utf-8')
        team.client = client

        id_team = team_exist(team, cur)
    
        if not id_team:
            client.sendall(b"F")
            continue

        team.id_team = id_team

        with teams_lock:
            if team_is_connected(team):
                client.sendall(b"A")
                continue
        return team
 

def handle_teams(team):
    while True: 
        try:
            msg_type : bytes | None = recv_data(team.client, 1)
            if msg_type is None: break
            msg_receiver : bytes | None = recv_data(team.client, 1)
            if msg_receiver is None: break

            if msg_type == b"G":
                msg_recv_id = int.from_bytes(msg_receiver, "big")
                get_team_name_by_id(msg_recv_id, team.client)
                continue

            msg_size : bytes | None= recv_data(team.client, 8)
            if msg_size is None: break
            size : int = int.from_bytes(msg_size, "big")
            msg : bytes | None = recv_data(team.client, size)
            if msg is None: break
            msg_recv_id = int.from_bytes(msg_receiver, "big")

            send_msg(team.id_team, msg_recv_id, msg_type, msg)
        except Exception as e:
            print("ERROR ", e)
            break


def send_msg(sender: int, receiver : int, msg_type, msg : bytes):
    data =  msg_type + sender.to_bytes(1, "big") + len(msg).to_bytes(8, "big") + msg

    team_recv = get_team(receiver)

    if team_recv is None: return
    try:
        team_recv.client.sendall(data)
    except Exception as e:
        print("Error ao enviar ", e)


def recv_data(client, size) -> bytes | None:
    data = b""
    while len(data) < size:
        pack = client.recv(size - len(data))
        if not pack:
            return None
        data += pack
    return data


def get_team_name_by_id(id, req):
    team_name : bytes = b""
    for team in teams:
        if team.id_team == id:
            team_name : bytes = team.name.encode("utf-8")
    data : bytes = \
    (len(team_name).to_bytes(1, "big") + team_name)
    req.sendall(data)


def team_is_connected(team) -> bool:
    for t in teams:
        if team.is_equal(t):
            return True
    return False


def team_exist(team, cur) -> bool | int:
    cur.execute(
        "SELECT id FROM equipes WHERE name=? AND password=?",
        (team.name, team.password)
    )
    res = cur.fetchone()
    if not res: return False

    return res[0]

def get_team(id) -> Team | None:
    with teams_lock:
        for team in teams:
            if team.id_team == id:
                return team


if __name__ == "__main__":
    start_server()

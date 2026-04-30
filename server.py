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


conn = sqlite3.connect("equipes.db")
cur = conn.cursor()


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as soc:
        print("Starting server...")
        soc.bind((HOST, PORT))
        soc.listen()
        while True:
            client, addr = soc.accept()
            team = login_team(client)
            teams.append(team)
            thread = threading.Thread(target=handle_teams, args=(team,))
            thread.start() 
            print(f"Client {addr} connected...")


def login_team(client) -> Team:
    while True:
        name_size_bytes : bytes | None = recv_data(client, 8)
        name_size_int = int.from_bytes(name_size_bytes, "big") 
        name : bytes = recv_data(client, name_size_int)
    
        password_size_bytes : bytes | None = recv_data(client, 8)
        passord_size_int = int.from_bytes(password_size_bytes, "big")
        password : bytes = recv_data(client, passord_size_int)
    
        team = Team()
        team.name = name.decode('utf-8')
        team.password = password.decode('utf-8')
        team.client = client
    
        if team_id:=team_exist(team):
            team.id_team = team_id
            client.sendall(b"T" + team_id.to_bytes(1, "big"))
            break
        else:
            client.sendall(b"F")
    return team
 

def handle_teams(team):
    while True: 
        try:
            msg_type : bytes = recv_data(team.client, 1)
            msg_receiver : bytes = recv_data(team.client, 1)
            if msg_type == b"G":
                msg_recv_id = int.from_bytes(msg_receiver, "big")
                get_team_name_by_id(msg_recv_id, team.soc)
                continue

            msg_size : bytes = recv_data(team.client, 8)
            size : int = int.from_bytes(msg_size, "big")
            msg : bytes = recv_data(team.client, size)
            msg_recv_id = int.from_bytes(msg_receiver, "big")

            send_msg(team.id_team, msg_recv_id, msg_type, msg)
        except:
            teams.remove(team)
            team.client.close()
            break


def send_msg(sender: int, receiver : int, msg_type, msg : bytes):
   data =  msg_type + sender.to_bytes(1, "big") + len(msg).to_bytes(8, "big") + msg

   for team in teams:
       if receiver == team.id_team:
           team_recv = get_team(receiver)
           if team_recv is None : return
           try:
               team_recv.client.sendall(data)
           except:
               teams.remove(team)


def recv_data(client, size) -> bytes:
    data = b""
    while len(data) < size:
        pack = client.recv(size - len(data))
        if pack is None:
            break
        data += pack
    return data


def get_team_name_by_id(id, req):
    team_name : bytes = b""
    for team in teams:
        if team.id == id:
            team_name : bytes = team.name.encode("utf-8")
    data : bytes = \
    (len(team_name).to_bytes(1, "big") + team_name)
    req.sendall(data)


def team_exist(team) -> bool | int:
    cur.execute(f"SELECT id FROM equipes WHERE name='{team.name}' AND password='{team.password}'")
    res = cur.fetchone()
    if not res: return False

    team = res[0]
    print(team)
    if team: return team
    return False


def get_team(id) -> Team | None:
    for team in teams:
        if team.id_team == id:
            return team


if __name__ == "__main__":
    start_server()

import socket
import threading

HOST = '0.0.0.0'
PORT = 12345

clients = []
names = {}

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    finally:
        s.close()

def broadcast_join(msg):
    for client in clients:
        try:
            client.sendall(msg.encode('utf-8'))
        except:
            clients.remove(client)

def handle_client(client):
    try:
        name = client.recv(1024).decode('utf-8')
        names[client] = name
        join_msg = f"📢 {name} さんが入室しました"
        broadcast_join(join_msg)

        while True:
            msg = client.recv(1024)
            if not msg:
                break
            for c in clients:
                if c != client:
                    c.sendall(msg)
    except:
        pass
    finally:
        if client in clients:
            clients.remove(client)
        client.close()

def main():
    ip = get_local_ip()
    print(f"サーバー起動中... IPアドレス: {ip} ポート: {PORT}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    while True:
        client, addr = server.accept()
        clients.append(client)
        threading.Thread(target=handle_client, args=(client,), daemon=True).start()

if __name__ == "__main__":
    main()

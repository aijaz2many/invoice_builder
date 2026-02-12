import socket

host = "ep-delicate-grass-a13wuz83-pooler.ap-southeast-1.aws.neon.tech"
try:
    ip = socket.gethostbyname(host)
    print(f"Successfully resolved {host} to {ip}")
except Exception as e:
    print(f"Failed to resolve {host}: {e}")

from boofuzz import *
import time

HOST = "127.0.0.1"
PORT = 5000

# ===== СЕССИЯ =====
session = Session(
    target=Target(
        connection=SocketConnection(HOST, PORT, proto='tcp')
    ),
    sleep_time=0.001
)

# ===== СПИСОК ENDPOINTS =====
endpoints = [
    "/",
    "/games",
    "/login",
    "/profile",
]

# ===== GET FUZZ =====
for ep in endpoints:
    name = f"GET {ep}"

    s_initialize(name)
    s_static(f"GET {ep}?input=")
    s_string("fuzz", fuzzable=True, max_len=50)
    s_static(" HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")

    session.connect(s_get(name))

# ===== POST FORM FUZZ =====
for ep in endpoints:
    name = f"POST {ep}"

    s_initialize(name)
    s_static(f"POST {ep} HTTP/1.1\r\n")
    s_static("Host: 127.0.0.1\r\n")
    s_static("Content-Type: application/x-www-form-urlencoded\r\n\r\n")

    s_string("username=", fuzzable=False)
    s_string("fuzzuser", fuzzable=True, max_len=30)
    s_string("&password=", fuzzable=False)
    s_string("fuzzpass", fuzzable=True, max_len=30)

    session.connect(s_get(name))

# ===== JSON FUZZ =====
for ep in endpoints:
    name = f"JSON {ep}"

    s_initialize(name)
    s_static(f"POST {ep} HTTP/1.1\r\n")
    s_static("Host: 127.0.0.1\r\n")
    s_static("Content-Type: application/json\r\n\r\n")

    s_static('{"input":"')
    s_string("fuzzjson", fuzzable=True, max_len=50)
    s_static('"}')

    session.connect(s_get(name))

# ===== ЗАПУСК НА ~1 ЧАС =====
start = time.time()
DURATION = 3600  # 1 час

session.fuzz()
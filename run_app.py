import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

def start_server():
    os.chdir(DIRECTORY)
    # find free port if 8080 is busy
    port = PORT
    for p in range(8080, 8095):
        try:
            with socketserver.TCPServer(("", p), Handler) as httpd:
                print(f"=====================================================")
                print(f"  ПББ Информатика Симуляторы сәтті іске қосылды!")
                print(f"  Сайт сілтемесі: http://localhost:{p}")
                print(f"  Тоқтату үшін: Ctrl + C басыңыз")
                print(f"=====================================================")
                webbrowser.open(f"http://localhost:{p}")
                httpd.serve_forever()
                break
        except OSError:
            continue

if __name__ == "__main__":
    start_server()

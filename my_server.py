from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.parse
import os
from datetime import datetime

# Configuration
HOST_NAME = 'localhost'
PORT = 8080
SECRET_PAGE_PATH = "secret"
LOG_FILE = "server_log.json"
MAIN_PAGE_FILE = 'index.html'
SECRET_PAGE_FILE = 'secret.html'
secret_pages=['/secret', '/admin','/user', '/home', '/accounts']

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def handle_request(self, method):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.read_file(MAIN_PAGE_FILE))
        elif parsed_path.path.startswith(f'/{SECRET_PAGE_PATH}'):
            if method == "POST":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                self.log_action(parsed_path.path, method, post_data.decode('utf-8'))
            else:
                self.log_action(parsed_path.path, method)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.read_file(SECRET_PAGE_FILE))

        elif parsed_path.path in secret_pages:
            if method == "POST":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                self.log_action(parsed_path.path, method, post_data.decode('utf-8'))
            else:
                self.log_action(parsed_path.path, method)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.read_file(SECRET_PAGE_FILE))   

        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><head><title>404 Not Found</title></head>")
            self.wfile.write(b"<body><h1>Page not found</h1></body></html>")

    def read_file(self, file_path):
        with open(file_path, 'r') as file:
            return file.read().encode('utf-8')

    def log_action(self, path, method, post_data=None):
        log_entry = {
            "path": path,
            "method": method,
            "client_address": self.client_address[0],
            "client_port": self.client_address[1],
            "timestamp": datetime.now().isoformat()
        }
        if post_data:
            log_entry["post_data"] = post_data

        if not os.path.isfile(LOG_FILE):
            with open(LOG_FILE, 'w') as log_file:
                json.dump([], log_file)
        with open(LOG_FILE, 'r+') as log_file:
            log_data = json.load(log_file)
            log_data.append(log_entry)
            log_file.seek(0)
            json.dump(log_data, log_file, indent=4)

def run(server_class=HTTPServer, handler_class=RequestHandler):
    server_address = (HOST_NAME, PORT)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on {HOST_NAME}:{PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()

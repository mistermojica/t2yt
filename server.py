import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

PORT = 3000

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parsear la URL y obtener los parámetros
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        # Imprimir los parámetros de la solicitud GET
        print("Solicitud GET recibida con los siguientes parámetros:", query_params)

        # Enviar una respuesta
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Hola, este es un servidor HTTP simple en Python!")

    def do_POST(self):
        # Obtener la longitud del contenido
        content_length = int(self.headers['Content-Length'])

        # Leer y imprimir el cuerpo de la solicitud POST
        post_data = self.rfile.read(content_length)
        print("Solicitud POST recibida con el siguiente cuerpo:", post_data.decode())

        # Enviar una respuesta
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Respuesta a la solicitud POST recibida!")

handler = SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), handler) as httpd:
    print("Servidor iniciado en el puerto ", PORT)
    httpd.serve_forever()

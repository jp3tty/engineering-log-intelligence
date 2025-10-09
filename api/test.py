from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            'message': 'Test endpoint working!',
            'psycopg2_available': False
        }
        
        try:
            import psycopg2
            response['psycopg2_available'] = True
        except ImportError as e:
            response['psycopg2_error'] = str(e)
        
        self.wfile.write(json.dumps(response).encode())
        return


import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi

class SecureFileUploader(BaseHTTPRequestHandler):
    ALLOWED_EXTENSIONS = ['jpg', 'png', 'txt', 'pdf']
    MAX_FILE_SIZE = 10 * 1024 * 1024
    UPLOAD_DIR = 'uploads/'

    def _validate_file(self, file_name, file_size):
        if file_size > self.MAX_FILE_SIZE:
            return False, "File size exceeds limit"
        if not any(file_name.lower().endswith(ext) for ext in self.ALLOWED_EXTENSIONS):
            return False, "File extension not allowed"
        return True, "File is valid"

    def _sanitize_file_name(self, file_name):
        # Remove unsupported characters
        safe_name = os.path.basename(file_name)
        return safe_name.replace(" ", "_")

    def _save_file(self, file_data, file_name):
        if not os.path.exists(self.UPLOAD_DIR):
            os.makedirs(self.UPLOAD_DIR)
        file_path = os.path.join(self.UPLOAD_DIR, file_name)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        return True, f"File {file_name} saved successfully"

    def do_POST(self):
        if self.path == '/upload':
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            file_item = form['file']

            if file_item.filename:
                file_name = self._sanitize_file_name(file_item.filename)
                file_data = file_item.file.read()
                is_valid, message = self._validate_file(file_name, len(file_data))
                if not is_valid:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(message.encode())
                    return
                
                self._save_file(file_data, file_name)
                self.send_response(200)
                self.end_headers()
                response_message = f"File '{file_name}' uploaded successfully."
                self.wfile.write(response_message.encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"No file was uploaded.")
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=SecureFileUploader, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Server running on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()

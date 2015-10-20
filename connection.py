import os
import urllib.parse
from time import gmtime, strftime

CONTENT_TYPE_SWITCH = {
        'ico': 'image/x-icon',
        'txt': 'text/plain',
        'html': 'text/html',
        'css': 'text/css',
        'js': 'application/javascript',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'swf': 'application/x-shockwave-flash'
}

class Connection:


    def __init__(self, client_connection, root_dir):
        self.client_connection = client_connection
        self.content_type = ''
        self.f = ''
        self.file_data = ''
        self.file_path = ''
        self.file_size = 0
        self.root_dir = root_dir or os.getcwd()
        self.request = ''
        self.request_method = ''
        self.status = '200 OK'

    def handle_request(self):

        self.request = self.client_connection.recv(1024)
        # self.request = b''
        # while True:
        #     data = self.client_connection.recv(1024)
        #     self.request += data
        #     if b'\r\n\r\n' in data:
        #         break
        if not self.request: return

        self.parse_request()

        http_response = 'HTTP/1.1 {status}\r\n'.format(status=self.status)
        http_response += 'Date: {date}\r\n'.format(date=strftime("%a, %d %b %Y %X GMT", gmtime()))
        http_response += 'Server: Technapache\r\n'
        http_response += 'Connection: keep-alive\r\n'
        if self.status == '200 OK':
            http_response += 'Content-Length: {length}\r\n'.format(length=self.file_size)
            http_response += 'Content-Type: {content_type}\r\n'.format(content_type=self.content_type)
        http_response += '\r\n'

        self.client_connection.sendall(http_response.encode())
        if (self.request_method != 'HEAD') and self.status == '200 OK':
            offset = 0
            blocksize = 4096

            while True:
                sent = os.sendfile(self.client_connection.fileno(), self.f.fileno(), offset, blocksize)
                if sent == 0:
                    break
                offset += sent
            self.f.close()

    def parse_request(self):
        splited_line = self.request.decode().split('\n', 1)[0].split(' ')
        request_method, request_uri = splited_line[0], splited_line[1]

        self.request_method = request_method
        if request_method not in ['GET', 'HEAD']:
            self.status = '405 Method not allowed'
            return
        request_path = request_uri.split('?')[0]
        request_path = urllib.parse.unquote(request_path)

        if '..' in request_uri:
            self.status = '400 Bad request'
            return
        self.file_path = self.root_dir + request_path

        splited_path = self.file_path.split('.')
        if len(splited_path) == 1:
            requesting_index = True
            file_extension = 'html'
            self.file_path += 'index.html'
        else:
            requesting_index = False
            file_extension = splited_path[-1]

        try:
            self.f = open(self.file_path, 'r')
            self.content_type = CONTENT_TYPE_SWITCH[file_extension.lower()]
            self.file_size = os.stat(self.file_path).st_size
        except IOError:
            if requesting_index:
                self.status = '403 Forbidden'
            else:
                self.status = '404 Not Found'

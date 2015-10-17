import os
import urllib.parse
from time import gmtime, strftime

class Connection:
	
	content_type_switch = {
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


	def __init__(self, client_connection, root_dir):
		self.root_dir = root_dir or os.getcwd()
		self.client_connection = client_connection
		self.file_data = ''


	def recieve_request(self):
		self.request = self.client_connection.recv(1024)

		self.handle_request()
		
		http_response = 'HTTP/1.1 {status}\r\n'.format(status=self.status)
		http_response += 'Date: {date}\r\n'.format(date=strftime("%a, %d %b %Y %X GMT", gmtime()))
		http_response += 'Server: Technoginx\r\n'
		http_response += 'Connection: close\r\n'	
		if self.status == '200 OK':
			http_response += 'Content-Length: {length}\r\n'.format(length=self.file_size)		
			http_response += 'Content-Type: {content_type}\r\n'.format(content_type = self.content_type)
		http_response += '\r\n'

		self.client_connection.sendall(http_response.encode())		
		if (self.request_method != 'HEAD') and self.status == '200 OK':		
			offset = 0
			blocksize = 4096

			while True:
				sent = os.sendfile(self.client_connection.fileno(), self.f.fileno(), offset, blocksize)
				if sent == 0:
					break  # EOF
				offset += sent
			self.f.close()



    # file = open("somefile", "rb")
    # blocksize = os.path.getsize("somefile")
    # sock = socket.socket()
    # sock.connect(("127.0.0.1", 8021))
    # offset = 0

    # while True:
    #     sent = sendfile(sock.fileno(), file.fileno(), offset, blocksize)
    #     if sent == 0:
    #         break  # EOF
    #     offset += sent



	def handle_request(self):
		request_method, request_uri, request_version = self.request.decode().split('\n', 1)[0].split(' ')		
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
		
		requesting_index = False
		splited_path = self.file_path.split('.')
		if len(splited_path) == 1:
			requesting_index = True
			file_extension = 'html'
		else:
			file_extension = splited_path[-1]

		if requesting_index == True:
			self.file_path += 'index.html'
			
		try: 
			self.f = open(self.file_path, 'r')			
			self.status = '200 OK'
			self.content_type = self.content_type_switch[file_extension.lower()]			
			self.file_size=os.stat(self.file_path).st_size
		except IOError:
			if requesting_index: self.status = '403 Forbidden'
			else: self.status = '404 Not Found'

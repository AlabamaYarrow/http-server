import os
import urllib
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
			http_response += 'Content-Length: {length}\r\n'.format(length=len(self.file_data))		
			http_response += 'Content-Type: {content_type}\r\n'.format(content_type = self.content_type)
		http_response += '\r\n'

		self.client_connection.sendall(http_response)		
		if (self.request_method != 'HEAD'):		
			self.client_connection.sendall(self.file_data)


	def handle_request(self):
		request_method, request_uri, request_version = self.request.split('\n', 1)[0].split(' ')		
		self.request_method = request_method
		if request_method not in ['GET', 'HEAD']:
			self.status = '405 Method not allowed'
			return 			
		request_path = request_uri.split('?')[0]
		request_path = urllib.unquote(request_path)
		
		if '..' in request_uri:
			self.status = '400 Bad request'
			return
		file_path = self.root_dir + request_path		
		
		requesting_index = False
		splited_path = file_path.split('.')
		if len(splited_path) == 1:
			requesting_index = True
			file_extension = 'html'
		else:
			file_extension = splited_path[-1]

		if requesting_index == True:
			file_path += 'index.html'
			
		try: 
			f = open(file_path, 'r')
			self.status = '200 OK'
			self.content_type = self.content_type_switch[file_extension.lower()]	
			self.file_data = f.read()
			f.close()
		except IOError:
			if requesting_index: self.status = '403 Forbidden'
			else: self.status = '404 Not Found'

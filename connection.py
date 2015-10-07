import os
from time import gmtime, strftime


class Connection:
	
	content_type_switch = {
		'ico': 'image/x-icon',
		'html': 'text/html',
		'css': 'text/css',
		'js': 'application/javascript',
		'jpg': 'image/jpeg',
		'jpeg': 'image/jpeg',
		'png': 'image/png',
		'gif': 'image/gif',
		'swf': 'application/x-shockwave-flash'
	}

	def __init__(self, client_connection):
		self.client_connection = client_connection

	def handle_request(self):
		request = self.client_connection.recv(1024)
		print request		
		request_uri = request.split('\n', 1)[0].split(' ')[1]
		self.send_response(request_uri)

	def send_response(self, request_uri):
		file_path = os.getcwd() + request_uri		
		file_extension = request_uri.split('.')[-1]		
		file_data = None
		if len(file_extension) == 0:
			status = '404 Not Found'
		else:
			try: 
				f = open(file_path, 'r')
				file_data = f.read()
				content_type = self.content_type_switch[file_extension]	
				print 'CONTENT TYPE' + content_type
				status = '200 OK'
			except IOError:		
				status = '404 Not Found'
		
		http_response = ''
		http_response += 'HTTP/1.1 {status}\n'.format(status=status)
		http_response += 'Date: {date}\n'.format(date=strftime("%a, %d %b %Y %X GMT", gmtime()))
		http_response += 'Server: Cherokee\n'
		http_response += 'Connection: close\n'	
		if status == '200 OK':
			http_response += 'Content-Length: {length}\n'.format(length=len(file_data))		
			http_response += 'Content-Type: text/html\n'
		http_response += '\n'

		self.client_connection.sendall(http_response)
		if status == '200 OK':
			self.client_connection.sendall(file_data)		
		self.client_connection.close()
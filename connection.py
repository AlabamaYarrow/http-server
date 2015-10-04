class Connection:
	def __init__(self, client_connection):
		self.client_connection = client_connection


	def handle_request(self):
		request = self.client_connection.recv(1024)
		print request
		self.send_response()


	def send_response(self):
		status = '200 OK'
		# status = '404 Not Found'

		http_response = 'HTTP/1.1 {status}\n'.format(status=status)
		http_response += '\n'
		http_response += 'Hello world!\n'

		print http_response

		self.client_connection.sendall(http_response)
		self.client_connection.close()
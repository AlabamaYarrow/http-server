#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import argparse
import os
import signal
import errno
from connection import Connection


def child_wait(signum, frame):
	while True:
		try:
			pid, status = os.waitpid(
				-1,         
				os.WNOHANG  
			)
		except OSError:
			return

	if pid == 0:  
		return


def main():
	parser = argparse.ArgumentParser(description='Python web server')
	parser.add_argument('-p', type = int, help='port number')
	parser.add_argument('-r', type = int, help='root directory')
	parser.add_argument('-c', type = int, help='CPU number')
	args = vars(parser.parse_args())

	host, port = '', args['p'] or 8888 
	root_directory = args['r'] or ''
	ncpu = args['c'] or 1

	listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listen_socket.bind((host, port))
	listen_socket.listen(1024)

	signal.signal(signal.SIGCHLD, child_wait)

	print ('CPU cores: {ncpu}'.format(ncpu=ncpu))
	print ('Running server on port {port}...'.format(port=port))

	while True:
		try:
			client_connection, client_address = listen_socket.accept()
		except IOError as e:
			code, msg = e.args            
			if code == errno.EINTR:
				continue
			else:
				raise		
		
		pid = os.fork()
		if pid == 0:
			listen_socket.close()
			connection = Connection(client_connection, root_directory)
			connection.recieve_request()
			os._exit(0)
		else:
			client_connection.close()

if __name__ == '__main__':
	main()

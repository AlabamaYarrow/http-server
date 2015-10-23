#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import argparse
import os
import signal
import errno
from connection import Connection


CPU_WORKER_RATIO = 25


def main():
	parser = argparse.ArgumentParser(description='Python web server')
	parser.add_argument('-p', type = int, help='port number')
	parser.add_argument('-r', type = str, help='root directory')
	parser.add_argument('-c', type = int, help='CPU number')
	args = vars(parser.parse_args())

	host, port = '', args['p'] or 8888
	root_directory = args['r'] or ''
	ncpu = args['c'] or 1

	listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listen_socket.bind((host, port))
	listen_socket.listen(1024)

	print('Running server on port {port}...'.format(port=port))
	print('CPU cores: {ncpu}'.format(ncpu=ncpu))
	print('Workers: {workers}'.format(workers=CPU_WORKER_RATIO * ncpu))
	
	forks = []

	for x in range(0, CPU_WORKER_RATIO * ncpu):
		pid = os.fork()
		forks.append(pid)
		if pid == 0:
			print('Running worker with PID:', os.getpid()) 
			while True:
				try:
					client_connection, client_address = listen_socket.accept()
				except IOError as e:
					code, msg = e.args
					if code == errno.EINTR:
						continue
					else:
						raise
				connection = Connection(client_connection, root_directory)
				connection.handle_request()
				client_connection.close()

	listen_socket.close()

	for pid in forks:
		os.waitpid(pid, 0)


if __name__ == '__main__':
	main()

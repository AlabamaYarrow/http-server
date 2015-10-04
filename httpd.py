#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import argparse
from threadpool import Threadpool
from connection import Connection

# * Отвечать следующими заголовками для успешных GET-запросов:
# * Date
# * Server
# * Content-Length
# * Content-Type
# * Connection
# * Корректный Content-Type для: .html, .css, js, jpg, .jpeg, .png, .gif, .swf
# * Понимать пробелы и %XX в именах файлов

def main():
	parser = argparse.ArgumentParser(description='Python web server')
	parser.add_argument('-p', type = int, help='port number')
	args = vars(parser.parse_args())

	host, port = '', args['p'] or 8888 

	listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listen_socket.bind((host, port))
	listen_socket.listen(1)

	print 'Running server on port {port}...'.format(port=port)

	while True:
		client_connection, client_address = listen_socket.accept()
		connection = Connection(client_connection)
		connection.handle_request()


if __name__ == '__main__':
	main()


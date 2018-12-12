#!/usr/bin/python3

import socket
import sys
import threading
import os
import ssl

list_lock = threading.Lock()
clients_list = []

"""def server_side_lis(ssl_client, ssl_send):
	while True:
		try:
			response = ssl_send.recv(65536)
			if not response:
				break
			ssl_client.send(response)	
		except:
			break
	ssl_send.close()
	ssl_client.close()"""

def client_side_lis(client_socket):
	request = client_socket.recv(65536).decode()
	print(request)
	try:
		if request.split()[0] != 'CONNECT':
			return
	except:
		return
	host = request.split()[1].split(':')[0]
	port = int( request.split()[1].split(':')[1])

	client_socket.send('HTTP/1.0 200 Connection established\r\n\r\n'.encode())
	
	cert_path = os.path.join(os.getcwd(),'cert', host + '.pem')

	print(cert_path)
	if not os.path.isfile(cert_path):
		os.system('cd cert && sh _make_site.sh ' + host)

	try:
		ssl_client = ssl.wrap_socket(client_socket, keyfile = cert_path, certfile = cert_path, server_side = True)
		ssl_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		client_socket.close()
		return

	try:
		ssl_send.connect((host, 443))
		ssl_send = ssl.wrap_socket(ssl_send, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE, ssl_version=ssl.PROTOCOL_SSLv23)
		ssl_request = ssl_client.recv(65536)
		print(ssl_request)
		ssl_send.send(ssl_request)

		#th = threading.Thread(target = server_side_lis, args = (ssl_client, ssl_send))
		#th.daemon = True
		#th.start()
		while True:
			try:
				response = ssl_send.recv(65536)
				print(response)
				if not response:
					break
				ssl_client.send(response)	
			except Exception as e:
				print(e)
				break

	except:
		print("***socket error***")
		ssl_client.close()
		ssl_send.close()
		client_socket.close()
		sys.exit(-1)

	ssl_send.close()
	ssl_client.close()

def start_proxy(server_socket):
	try:
		while True:
			(client_socket,addr) = server_socket.accept()
			list_lock.acquire()
			clients_list.append(client_socket)
			list_lock.release()
			t = threading.Thread(target = client_side_lis, args = (client_socket,))
			t.daemon = True
			t.start()
	except KeyboardInterrupt:
		print("\n--- Server Closed ---")
		list_lock.acquire()
		for client in clients_list:
			client.close()
		list_lock.release()
		server_socket.close()
		sys.exit(1)

def main():
	if len(sys.argv) != 2:
		print("*** Syntax Error ***")
		print("Syntax: http_proxy <port>")
		print("Sample: http_oroxy 8080")
		sys.exit(1)

	port = int(sys.argv[1])

	#os.system('cd cert && sh _clear_site.sh')
	#os.system('cd cert && sh _init_site.sh')
    
	server_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(('127.0.0.1',port))
	server_socket.listen(10)
	
	start_proxy(server_socket)

if __name__ == '__main__':
	main()
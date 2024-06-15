#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import os
from NetworkApplications import NetworkApplication

class WebServer(NetworkApplication):

    def handleRequest(tcpSocket):
        # 1. Receive request message from the client on connection socket
        sentence = tcpSocket.recv(2048).decode()
        # 2. Extract the path of the requested object from the message (second part of the HTTP header)
        path = sentence.split(" ")[1][1:]
        # 3. Read the corresponding file from disk
        os.chdir("./")
        file_content = ""
        try:
            with open(path, 'r') as file:
                # 4. Store in temporary buffer
                file_content = file.read()
            response_proto = 'HTTP/1.1'
            response_status = '200'
            response_status_text = 'OK'
        except:
            with open("html/pagenotfound.html", 'r') as file:
                # 4. Store in temporary buffer
                file_content = file.read()
            response_proto = 'HTTP/1.1'
            response_status = '404'
            response_status_text = 'NOT FOUND'

        # 5. Send the correct HTTP response error
        tcpSocket.send(('%s %s %s\n' % (response_proto, response_status, response_status_text)).encode('utf-8'))

        # 6. Send the content of the file to the socket
        response_body = file_content
        response_headers = {
            'Content-Type': 'text/html; encoding=utf8',
            'Content-Length': len(response_body),
            'Connection': 'close',
        }
        response_headers_raw = ''.join('%s: %s\n' % (k, v) for k, v in response_headers.items())
        tcpSocket.send(response_headers_raw.encode('utf-8'))
        tcpSocket.send('\n'.encode('utf-8'))
        tcpSocket.send(response_body.encode('utf-8'))
        # 7. Close the connection socket
        tcpSocket.close()

    def __init__(self, args):
        try:
            print('Web Server starting on port: %i...' % (args.port))
            # 1. Create server socket
            serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 2. Bind the server socket to server address and server port
            serverSocket.bind(('', args.port))
            # 3. Continuously listen for connections to server socket
            serverSocket.listen()
            connectionSocket = None
            while True:
                connectionSocket, addr = serverSocket.accept()
                # 4. When a connection is accepted, call handleRequest function, passing new connection socket (see https://docs.python.org/3/library/socket.html#socket.socket.accept)
                WebServer.handleRequest(connectionSocket)
        # 5. Close server socket
        except KeyboardInterrupt:
            print('Interrupted')
            connectionSocket.close()
            serverSocket.close()
        except Exception as e:
            print("caught exception")
            print(e)
            connectionSocket.close()
            serverSocket.close()
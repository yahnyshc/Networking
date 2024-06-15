#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import random
import os
from NetworkApplications import NetworkApplication

class Proxy(NetworkApplication):

    def contactServer(request):
        path = request.split(" ")[1]
        webserver = path.split("://")[1].split("/")[0]
        print("Contacting " + webserver + " to get response.")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((webserver, 80))
            s.send(request.encode('utf-8'))
        except:
            print("Problem connecting to the server.")
            return None
        response = ""
        while True:
            try:
                s.settimeout(3)
                data = s.recv(9999999).decode('utf-8')
            except:
                break
            if (len(data) > 0):
                response += data
            else:
                break
        s.close()
        return response

    def generateRandomCachename(self):
        return "./ProxyCache/" + str(int(random.random() * (1000000000)))

    def cacheResponse(self, request, response):
        if response is None:
            return
        filename = self.generateRandomCachename()
        while (os.path.isfile(filename)):
            filename = self.generateRandomCachename()

        os.chdir("./")
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "w") as cachedResponse:
                cachedResponse.write(response)
            self.cache[request] = filename
            print("Cached response under " + filename)
        except Exception as e:
            print("Failed to cache response.")
            print(e.message)

    def handleRequest(self, tcpSocket):
        request = tcpSocket.recv(9999999).decode('utf-8')
        print("\nRequest:")
        print(request)
        os.chdir("./")
        if request in self.cache:
            try:
                with open(self.cache[request], 'r') as file:
                    response = file.read()
                    print("got response from cache.")
            except:
                response = Proxy.contactServer(request)
                self.cacheResponse(request, response)
        else:
            response = Proxy.contactServer(request)
            self.cacheResponse(request, response)

        tcpSocket.sendall(response.encode('utf-8'))
        # Close the connection socket
        tcpSocket.close()

    def __init__(self, args):
        self.cache = {}
        try:
            print('Web Proxy starting on port: %i...' % (args.port))
            # 1. Create proxy socket
            proxySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 2. Bind the proxy socket to address and port
            proxySocket.bind(('', args.port))
            # 3. Continuously listen for connections to server socket
            proxySocket.listen()
            connectionSocket = None
            while True:
                connectionSocket, addr = proxySocket.accept()
                # 4. When a connection is accepted, call handleRequest function, passing new connection socket
                self.handleRequest(connectionSocket)
        # 5. Close server socket
        except KeyboardInterrupt:
            print('Interrupted')
        except Exception as e:
            print("caught exception")
            print(e.message)
        connectionSocket.close()
        proxySocket.shutdown(socket.SHUT_RDWR)
        proxySocket.close()
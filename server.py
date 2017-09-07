import os
import select
import socket
import sys
import threading
import serverClient as Client

class Server:
    
    def __init__(self):
        print('Starting server')
        self.host = ''
        self.port = 50010
        self.backlog = 10
        self.size = 2048
        self.server = None
        self.threads = []
        self.data=[[],[],[]]
        
        self.open_socket()
        input = [self.server,sys.stdin]

    def open_socket(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host,self.port))
            self.server.listen(60)
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        inputready,outputready,exceptready = select.select(input,[],[])
        for s in inputready:

            if s == self.server:
                # handle the server socket
                c = Client.Client(self.server.accept())
                c.start()
                self.threads.append(c)
                

            elif s == sys.stdin:
                # handle standard input
                junk = sys.stdin.readline()
                running = 0
                
                    

        # close all threads

    def close(self):
        self.server.close()
        for c in self.threads:
            c.join()
            
            


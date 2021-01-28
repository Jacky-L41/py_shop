#!/usr/bin/env python3.3
# acctclient.py

import socket
import os, sys, time,random
import signal
import threading


def send_request(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip,port))
        sock.sendall(bytes(" ".join(message), 'utf-8'))
        response = str(sock.recv(1024), 'utf-8')
        print(response)

def client(ip,port,client_id):
    send_request(ip,port,("START "+str(client_id)).split())                             # Start shopping as user <client_id>
    time.sleep(random.random()*2)
    send_request(ip,port,("UPDATE "+str(client_id)+" 2 20").split())                    # User set 20 of <product_id:2> in cart
    time.sleep(random.random()*2)
    send_request(ip,port,("REPLENISH 2 10").split())                                    # User replenish item <product_id:2>, add 10 to stock
    time.sleep(random.random()*2)
    send_request(ip,port,("UPDATE "+str(client_id)+" 3 8").split())                     # User set 8 of <product_id:3> in cart
    time.sleep(random.random()*2)
    send_request(ip,port,("REPLENISH 3 5").split())                                     # User replenish item <product_id:3>, add 2 to stock
    time.sleep(random.random()*2)
    send_request(ip,port,("UPDATE "+str(client_id)+" 3 8").split())                     # User set 8 of <product_id:3> again simulating lack of stock from previous attempt
    time.sleep(random.random()*2)
    send_request(ip,port,("CART "+str(client_id)).split())                              # Get current shopping cart info of current user
    time.sleep(random.random()*2)
    send_request(ip,port,("PAY "+str(client_id)+" 1234123412341234 02/12").split())     # User check out shopping cart


        
if __name__ == "__main__":
    ip,port="localhost", 11906
    threads = [threading.Thread(target=client,args=(ip,port,i)) for i in range(1,5)]    # Simulate 4 customers shopping at the same time
    [aThread.start() for aThread in threads]
    [aThread.join() for aThread in threads]





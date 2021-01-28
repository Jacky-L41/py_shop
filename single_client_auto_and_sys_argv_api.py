#!/usr/bin/env python3.3
# acctclient.py

import socket
import os, sys, time,random
import signal


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip,port))
        sock.sendall(bytes(" ".join(message), 'utf-8'))
        response = str(sock.recv(1024), 'utf-8')
        print(response)

        
if __name__ == "__main__":
    ip,port="localhost", 11906
    if(len(sys.argv)<2):
        print("Usage:",sys.argv[0], "<API QUERY>")
        print("API example: START <client_id>")
        print("API example: UPDATE <client_id> <product_id> <quantity>")
        print("API example: PAY <client_id> <card num> <expiry date>")
        print("API example: REPLENISH <product_id> <quantity>")
        print("API example: CART <client_id>")
        print("API example: CLEAR <client_id>")
        print("example: START 1")
        print("example: UPDATE 1 2 20")
        print("example: UPDATE 1 3 8")
        print("example: PAY 1 1234123412341234 02/12")
        print("example: REPLENISH 2 10")
        print("example: CART 1")
        print("example: CLEAR 1")
        print("Running test cases above")
        client(ip,port,"START 1".split())
        client(ip,port,"UPDATE 1 2 20".split())
        client(ip,port,"UPDATE 1 3 8".split())
        client(ip,port,"PAY 1 1234123412341234 02/12".split())
        client(ip,port,"REPLENISH 2 10".split())
        client(ip,port,"CART 1".split())
        client(ip,port,"CLEAR 1".split())
    else:
        client(ip, port, sys.argv[1:])





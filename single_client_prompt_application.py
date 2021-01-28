#!/usr/bin/env python3.3
# acctclient.py

import socket
import os, sys, time,random
import signal,json
from functools import partial

def expireSession(ip,port,client_id,signal,frame):
    result=send_request(ip,port,"CLEAR "+client_id)
    print("[-] Session expired, clearing shopping cart")
    print(result)
    raise Exception("[-] Exit Application")

def send_request(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip,port))
        sock.sendall(bytes(message, 'utf-8'))
        response = str(sock.recv(1024), 'utf-8')
        sock.close()
        return response

def client(ip,port):
    print("[?] Please enter your client ID: ", end='')
    client_id = input()
    result = json.loads(send_request(ip,port,"START "+client_id))
    if result["exist"] == True:
        signal.signal(signal.SIGALRM, partial(expireSession,ip,port,client_id))
        try:
            while True:
                signal.alarm(15)
                print("[+] ==================================== [+]")
                print("[+] Welcome! current client ID is", client_id)
                print("[1] View your current shopping cart")
                print("[2] Update your shopping cart")
                print("[3] Checkout (Pay)")
                print("[4] Replenish products")
                print("[5] Switch user without checkout (Start)")
                print("[6] Exit application without checkout")
                print("[?] Please enter (1,2,3,4,5,6): ",end='')
                action = input()
                if action == "1":
                    result=send_request(ip,port,"CART "+client_id)
                    print(result)
                if action == "2":
                    print("[!] Usage: <product_id> <quantity>")
                    msg = input("[?] Please enter (1 2): ")
                    msg = "UPDATE " + client_id + " " + msg 
                    print(send_request(ip,port,msg))
                if action == "3":
                    print("[!] Usage: <card_num> <expiry_date>")
                    msg = input("[?] Please enter (8888777766665555 12/23): ")
                    msg = "PAY " + client_id + " " + msg 
                    print(send_request(ip,port,msg))
                if action == "4":
                    print("[!] Usage: <product_id> <quantity>")
                    msg = input("[?] Please enter (1 2): ")
                    msg = "REPLENISH " + msg 
                    print(send_request(ip,port,msg))
                if action == "5":
                    print("[!] Cleaning chopping cart of current client_id")
                    result=send_request(ip,port,"CLEAR "+client_id)
                    print(result)
                    print("[?] Please enter your client ID: ", end='')
                    temp_id = input()
                    result = json.loads(send_request(ip,port,"START "+client_id))
                    if True in result.values():
                        client_id=temp_id
                if action == "6":
                    print("[!] Cleaning chopping cart of current client_id")
                    result=send_request(ip,port,"CLEAR "+client_id)
                    print(result)
                    print("Bye! Hope I can get a good mark :D")
                    break
        except Exception as exc:
            print(exc)

if __name__ == "__main__":
    ip,port="localhost", 11906
    client(ip, port)





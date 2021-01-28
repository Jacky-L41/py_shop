#!/usr/bin/env python3.3
# acctserv.py
from socketserver import BaseRequestHandler, TCPServer
from functools import partial
import socketserver, socket
import signal
import threading
import sqlite3
import json
import time,random


class ThreadedTCPRequestHandler(BaseRequestHandler):
    def setup(self):
        self.conn=sqlite3.connect('database.db')

    def handleStart(self,id):
        c = self.conn.cursor()
        cursor = c.execute("SELECT client_id from clients")
        result = {"exist": False}
        for row in cursor:
            if int(id) == row[0]:
                result["exist"]=True
                result["client_id"]=id
                break
        return json.dumps(result)
   
    def handleUpdate(self,client_id,product_id, qty):
        self.lock.acquire()
        c = self.conn.cursor()
        curr_time = time.time()
        cursor = c.execute("SELECT quantity from products where product_id=?",(product_id,))
        quantity, subtotal, amount, lastqty = 0, 0, 0, 0
        result = {"msg":"Failed updating shopping cart: Not enough quantity", "product_id": product_id}
        for row in cursor:
            quantity = row[0]
        cursor = c.execute("SELECT quantity from carts where client_id=? and product_id=?", (client_id,product_id))
        if cursor.rowcount != 0:
            for row in cursor:
                lastqty = row[0]
        if int(qty)-lastqty <= quantity:
            if(int(qty)==0):
                c.execute("DELETE from carts where client_id=? and product_id=?",(client_id,product_id))
            else:
                c.execute("INSERT into carts values (?,?,?,?) on conflict (carts.client_id,carts.product_id) do update set quantity=?",(client_id,product_id,int(qty),curr_time,int(qty)))
            self.conn.commit()
            c.execute("UPDATE products set quantity=quantity-(?) where product_id=?",(int(qty)-lastqty,product_id))
            self.conn.commit()
            cursor = c.execute("SELECT c.quantity, p.price from carts c, products p where client_id=? and c.product_id=p.product_id",(client_id,))
            for row in cursor:
                amount = amount + int(row[0])
                subtotal = subtotal + float(row[1])*int(row[0])
            result["msg"] = "Success"
            result["cart_owner_id"] = client_id
            result["total_amount"] = amount
            result["subtotal"] = subtotal
            result["update_GMT_time"] = str(curr_time)
            result["available"] = quantity - (int(qty) - lastqty)
        else:
            result["product_id"] = product_id
            result["available"] = quantity
        self.lock.release()
        return json.dumps(result)

    def handlePay(self,client_id,card_num,expiry_date):
        result = {"success": False,"cart_owner_id": client_id}
        try:
            card_no = int(card_num)
            month, year = expiry_date.split('/')
            if month[0]=='0':
                month = month[1:]
            if year[0]=='0':
                year = year[1:]
            mm,yy=int(month),int(year)
            if (mm >= 1 and mm <= 12) and (yy >= 0 and yy <= 99) and len(card_num)==16:
                self.lock.acquire()
                c = self.conn.cursor()
                c.execute("DELETE from carts where client_id=?",(client_id,))
                self.conn.commit()
                self.lock.release()
                result["success"] = True
                result["msg"] = "Successfully paid, shopping cart cleared."
            else:

                result["success"] = False
            return json.dumps(result)
        except ValueError:
            return json.dumps(result)

    def handleReplenish(self,product_id, qty):
        result = {"success":False,"product_id":product_id}
        try:
            quantity = int(qty)
            new_qty = quantity
            if(quantity>=0):
                self.lock.acquire()
                c = self.conn.cursor()
                c.execute("UPDATE products set quantity=quantity+? where product_id=?",(quantity,product_id))
                self.conn.commit()
                cursor = c.execute("SELECT quantity from products where product_id=?", (product_id,))
                for row in cursor:
                    new_qty = row[0]
                    break
                result["available"] = new_qty
                result["success"] = True
                self.lock.release() 
        except Exception as ex:
            result["success"] = False
        return json.dumps(result)

    def handleClear(self,client_id):
        result = {"success":False,"client_id":client_id}
        c = self.conn.cursor()
        self.lock.acquire()
        cursor = c.execute("SELECT product_id,quantity from carts where client_id=?",(client_id,))
        records=list()
        for row in cursor:
            records.append((row[0],row[1]))
        for aRecord in records:
            c.execute("UPDATE products set quantity=quantity+? where product_id=?",(aRecord[1],aRecord[0]))
            self.conn.commit()
        c.execute("DELETE from carts where client_id=?",(client_id,))
        self.conn.commit()
        self.lock.release()
        result["success"]=True
        result["msg"]="Shopping cart cleared"
        
        return json.dumps(result)
    
    def handleCart(self,client_id):
        result = {"client_id":client_id}
        result["items"] = list()
        total = 0.0
        c = self.conn.cursor()
        cursor = c.execute("SELECT c.product_id,c.quantity,p.price from carts c, products p where client_id=? and c.product_id=p.product_id",(client_id,))
        for row in cursor:
            result["items"].append({"product_id": row[0], "quantity": row[1], "subtotal": float(row[1])*float(row[2])})
            total = total + float(row[1])*float(row[2])
        result["total"] = total
        return json.dumps(result)

    def handle(self):
        print('[Server] Got connection from', self.client_address)
        # while True:
        msg = self.request.recv(1024).decode("utf=8")
        return_msg = "Usage: \nSTART <client_id> \nUPDATE <client_id> <product_id> <quantity> \nPAY <client_id> <card_num> <expiry_date> \nCART <client_id> \nREPLENISH <product_id> <quantity> \nCLEAR <client_id>"
        action = msg.split()
        if len(action)<2:
            return
        if action[0]=="START" and len(action)==2 and action[1].isdigit():
            return_msg=self.handleStart(action[1])

        if action[0]=="UPDATE" and len(action)==4 and action[1].isdigit() and action[2].isdigit() and action[3].isdigit():
            return_msg=self.handleUpdate(action[1], action[2], action[3])

        if action[0]=="PAY" and len(action)==4 and action[1].isdigit() and action[2].isdigit() and len(action[3][:2]) == 2 and len(action[3][3:]) == 2 and action[3][:2].isdigit() and action[3][3:].isdigit():
            return_msg=self.handlePay(action[1], action[2], action[3])

        if action[0]=="REPLENISH" and len(action)==3 and action[1].isdigit() and action[2].isdigit():
            return_msg=self.handleReplenish(action[1], action[2])

        if action[0]=="CLEAR" and len(action) == 2 and action[1].isdigit():
            return_msg=self.handleClear(action[1])

        if action[0]=="CART" and len(action) == 2 and action[1].isdigit():
            return_msg=self.handleCart(action[1])

        self.request.send(bytes(return_msg, 'utf-8'))
    def finish(self):
        self.conn.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    # pass
    def __init__(self, address_tuple, handler, aLock):
        super().__init__(address_tuple, handler)
        handler.lock=aLock


def server(ip, port):
    lock = threading.Lock()
    tcpServer = ThreadedTCPServer((ip,port), ThreadedTCPRequestHandler, lock)
    server_thread = threading.Thread(target=tcpServer.serve_forever)
    # server_thread.daemon = True
    server_thread.start()
    print("[Server] TCP server loop running in thread:", server_thread.name)
    print("[Server] Listening address", str(tcpServer.server_address[0])+":"+str(tcpServer.server_address[1]))
    return tcpServer.server_address

if __name__ == "__main__":
    address = server('localhost', 11906)




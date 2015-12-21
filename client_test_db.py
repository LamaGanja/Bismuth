import time
import ast
import hashlib
import socket
import re
import sqlite3
import os
import sys

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random

if os.path.isfile("keys.pem") is True:
    print "keys.pem found"

else:   
    #generate key pair and an address
    random_generator = Random.new().read
    key = RSA.generate(1024, random_generator)
    public_key = key.publickey()

    private_key_readable = str(key.exportKey())
    public_key_readable = str(key.publickey().exportKey())
    address = hashlib.sha224(public_key_readable).hexdigest() #hashed public key
    #generate key pair and an address

    print "Your address: "+ str(address)
    print "Your private key:\n "+ str(private_key_readable)
    print "Your public key:\n "+ str(public_key_readable)

    pem_file = open("keys.pem", 'a')
    pem_file.write(str(private_key_readable)+"\n"+str(public_key_readable) + "\n\n")
    pem_file.close()
    address_file = open ("address.txt", 'a')
    address_file.write(str(address)+"\n")
    address_file.close()


# import keys
key_file = open('keys.pem','r')
key = RSA.importKey(key_file.read())
public_key = key.publickey()
private_key_readable = str(key.exportKey())
public_key_readable = str(key.publickey().exportKey())
address = hashlib.sha224(public_key_readable).hexdigest()

print "Your address: "+ str(address)
print "Your private key:\n "+ str(private_key_readable)
print "Your public key:\n "+ str(public_key_readable)
# import keys


#network client program
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#open peerlist and connect
with open ("peers.txt", "r") as peer_list:
    peers=peer_list.read()
    peer_tuples = re.findall ("'([\d\.]+)', '([\d]+)'",peers)
    print peer_tuples

connected = 0
while connected == 0:
    for tuple in peer_tuples:
        HOST = tuple[0]
        #print HOST
        PORT = int(tuple[1])
        #print PORT

        try:
            s.connect((HOST, PORT))
            connected = 1
            print "Connected to "+str(HOST)+" "+str(PORT)
            break
        except:
            print "Cannot connect to "+str(HOST)+" "+str(PORT)
            pass

#open peerlist and connect


s.sendall('Hello, server')

peer = s.getpeername()
data = s.recv(1024) #receive data
print 'Received data from '+ str(peer) +"\n"+ str(data)

#get remote peers into tuples
server_peer_tuples = re.findall ("'([\d\.]+)', '([\d]+)'",data)
print server_peer_tuples
print len(server_peer_tuples)
#get remote peers into tuples

#get local peers into tuples
peer_file = open("peers.txt", 'r')
peer_tuples = []
for line in peer_file:
    extension = re.findall ("'([\d\.]+)', '([\d]+)'",line)
    peer_tuples.extend(extension)
peer_file.close()
print peer_tuples
#get local peers into tuples

for x in server_peer_tuples:
    if x not in peer_tuples:
        print str(x)+" is a new peer, saving."

        peer_list_file = open("peers.txt", 'a')
        peer_list_file.write(x+"\n")
        peer_list_file.close()        
        
    else:
        print str(x)+" is not a new peer, skipping."


        
#broadcast
con = None
try:
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    c.execute("SELECT block_height FROM transactions ORDER BY block_height DESC LIMIT 1;")
    block_height = int(c.fetchone()[0])   
    block_height_new = block_height+1

    #request block update
    s.sendall (str(block_height))
    #request block update
    
except sqlite3.Error, e:                        
    print "Error %s:" % e.args[0]
    sys.exit(1)                        
finally:                        
    if conn:
        conn.close()       

to_address = "dummy2"
amount = 3

transaction = str(block_height_new) +":"+ str(address) +":"+ str(to_address) +":"+ str(amount)
signature = key.sign(transaction, '')
print "Signature: "+str(signature)

if public_key.verify(transaction, signature) == True:
    print "The signature is valid, proceeding to send transaction, signature and the public key"
    s.sendall(transaction+";"+str(signature)+";"+public_key_readable)

else:
    print "Invalid signature"


#sync from node
#request block update
s.sendall (str(block_height))
#request block update
    
block_difference = s.recv(1024)
print "Receiving "+block_difference+" steps to sync"
i = 1
while int(i) <= int(block_difference):
    sync = s.recv(1024)
    i = i+1
    #verify
    sync_list = ast.literal_eval(sync) #this is great, need to add it to client -> node sync
    received_block_height = sync_list[0]
    received_address = sync_list[1]
    received_to_address = sync_list[2]
    received_amount = sync_list [3]
    received_signature = sync_list[4]
    received_public_key_readable = sync_list[5]
    received_public_key = RSA.importKey(sync_list[5])
    received_transaction = str(received_block_height) +":"+ str(received_address) +":"+ str(received_to_address) +":"+ str(received_amount) #todo: why not have bare list instead of converting?

    received_signature_tuple = ast.literal_eval(received_signature) #converting to tuple
    if received_public_key.verify(received_transaction, received_signature_tuple) == True:
        print "Received step "+str(received_block_height)+" is valid"
        #verify
        #save step to db
        con = None
        try:
            conn = sqlite3.connect('test.db')
            c = conn.cursor()
            c.execute("INSERT INTO transactions VALUES ('"+str(received_block_height)+"','"+str(received_address)+"','"+str(received_to_address)+"','"+str(received_to_address)+"','"+str(received_signature)+"','"+str(received_public_key_readable)+"')") # Insert a row of data
            print "Ledger updated with a received transaction"
            
        except sqlite3.Error, e:                        
            print "Error %s:" % e.args[0]
            sys.exit(1)                        
        finally:                        
            if conn:
                conn.close()
        #save step to db
        print "Ledger synchronization finished"
    
#sync from node
    
#broadcast
s.close()

#network client program

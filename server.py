import socket
import sys
import re
import ast
import sqlite3

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 2829)
print 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print 'waiting for a connection'
    connection, client_address = sock.accept()

    talkie = 0
    try:
        print 'connection from', client_address

        # Receive and send data
        while True:
            hello = connection.recv(4096)
            print 'received '+ hello
            
            if hello:
                with open ("peers.txt", "r") as peer_list:
                    peers=peer_list.read()
                    print peers
                    connection.sendall(peers)
                    
            data = connection.recv(4096)
            if data:
                data_split = data.split(";")
                received_transaction = data_split[0]
                print "Received transaction: "+received_transaction
                #split message into values
                received_transaction_split = received_transaction.split(":")
                block_height = received_transaction_split[0]
                address = received_transaction_split[1]
                to_address = received_transaction_split[2]
                amount =received_transaction_split[3]
                #split message into values
                received_signature = data_split[1] #needs to be converted
                received_signature_tuple = ast.literal_eval(received_signature) #converting to tuple
                print "Received signature: "+received_signature
                received_public_key_readable = data_split[2]
                print "Received public key: "+received_public_key_readable

                #convert received strings
                received_public_key = RSA.importKey(received_public_key_readable)
                #convert received strings
                
                if received_public_key.verify(received_transaction, received_signature_tuple) == True:
                    print "The signature is valid"
                    #transaction processing
                    con = None
                    try:
                        conn = sqlite3.connect('thincoin.db')
                        c = conn.cursor()
                        c.execute('''SELECT block_height FROM transactions ORDER BY block_height DESC LIMIT 1;''')
                        block_latest = c.fetchone()[0]
                        print "Latest block in db: "+block_latest
                        if block_height != int(block_latest)+1:
                            print "Block height invalid"
                        # Create table
                        c.execute('''CREATE TABLE IF NOT EXISTS transactions (block_height, address, to_address, amount)''')
                        # Insert a row of data
                        c.execute("INSERT INTO transactions VALUES ('"+block_height+"','"+address+"','"+to_address+"','"+amount+"')")
                        # Save (commit) the changes
                        conn.commit()
                        print "Saved"
                    except sqlite3.Error, e:                        
                        print "Error %s:" % e.args[0]
                        sys.exit(1)                        
                    finally:                        
                        if conn:
                            conn.close()    
                    #transaction processing
                else:
                    print "Signature invalid"

 
            else:
                print 'no more data from', client_address
                break
            
    finally:
        # Clean up the connection
        connection.close()

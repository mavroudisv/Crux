
import binascii
import struct
import config as conf

import zlib
import base64
import sys


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    
    if conf.COMPRESS:
        msg = zlib.compress(msg)
        #msg = base64.b64encode(msg)
    
    if conf.SHOW_LEN:    
        print "len: " + str(len(msg))
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
        
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
        
        
    if conf.COMPRESS and n != 4:
        try:
            data = zlib.decompress((data))
        except Exception as e:
            print "Exception while decompressing: " + str(e)

        #print n
        #print len(data)
    return data

from petlib.ec import *
import binascii

import SocketServer
import socket
import json
import sys
import math
import sys
import traceback
import threading

import config as conf
import utilities
import Classes
import SocketExtend as SockExt
import operations as op


#Compute Median	
def median_operation(sk_sum, auths):
	proto = Classes.get_median(sk_sum, min_b = 0, max_b = 1000, steps = 20) #Compute Median
	plain = None
	while True:
		v = proto.send(plain)
		if isinstance(v, int):
			break
		
		plain = collective_decryption(v, auths)
		#print "*: " + str(plain)

	#print "Estimated median: " + str(v)
	return str(v)



def mean_operation(sk_sum, auths):
    try:
        lower_bound = 0
        upper_bound = 120
        
        keys = [i for i in range(lower_bound, upper_bound)]
        
        #Find mean
        enc_sum_mul = (sk_sum.estimate(keys[0])[0]).__rmul__(keys[0])
        enc_sum = sk_sum.estimate(keys[0])[0]
        
        for i in keys[1:]:
            print "est: " + str(collective_decryption(enc_sum_mul, auths)) #To check if it exceeds the db size
            enc_sum_mul = enc_sum_mul.__add__(sk_sum.estimate(i)[0].__rmul__(i))
            enc_sum += sk_sum.estimate(i)[0]
    
        plain_sum_mul = float(collective_decryption(enc_sum_mul, auths))
        plain_sum = float(collective_decryption(enc_sum, auths))
    
        mean = float(plain_sum_mul)/float(plain_sum)
        print "mean: " + str(mean)
    
    except Exception as e:
        print "Exception while computing mean: ", e
       
    return  str(float(plain_sum_mul)/float(plain_sum-1))



def variance_operation(sk_sum, auths):    
    try:
        lower_bound = 0
        upper_bound = 120
        
        keys = [i for i in range(lower_bound, upper_bound)]
        
        #Find mean
        enc_sum_mul = (sk_sum.estimate(keys[0])[0]).__rmul__(keys[0])
        enc_sum = sk_sum.estimate(keys[0])[0]
        
        for i in keys[1:]:
            #print "est: " + str(collective_decryption(enc_sum_mul, auths))
            enc_sum_mul = enc_sum_mul.__add__(sk_sum.estimate(i)[0].__rmul__(i))
            enc_sum += sk_sum.estimate(i)[0]
    
        plain_sum_mul = float(collective_decryption(enc_sum_mul, auths))
        plain_sum = float(collective_decryption(enc_sum, auths))
    
        mean = float(plain_sum_mul)/float(plain_sum)
        print "mean: " + str(mean)
        
        ###################
        
        #Sum of differences
        plain_sum_diffs = 0
        N = 0
        for i in keys:
            #print "est: " + str(collective_decryption(enc_sum_mul, auths))
            tmp_res = (i - mean)**2
            plain_sum_diffs += (tmp_res * float(collective_decryption(sk_sum.estimate(i)[0], auths)))
            
        
        #Divide with plain_sum
        variance = float(plain_sum_diffs)/float(plain_sum)
        
    except Exception as e:
        print "Exception while computing mean: ", e
       
    return  str(variance)


def collective_decryption(ct, auths=[]):
	
	try:
		print "A"
		#Generate ephimeral key
		G = EcGroup(nid=conf.EC_GROUP)
		tmp_priv = G.order().random()
		tmp_pub = tmp_priv * G.generator()
		print "B"
		#Encrypt with ephimeral key
		enc_ct = Classes.Ct.enc(tmp_pub, ct)
		print "C"
		print "ct.m: " + str(enc_ct.m)
		for auth in auths: #Send for decryption to each authority
			print "D"
			json_obj_str = enc_ct.to_JSON()
			data = {'request':'partial_decrypt', 'contents': json_obj_str}
			#print data
			
			print "E"
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((auth, conf.AUTH_PORT)) #connect to authority
			SockExt.send_msg(s, json.dumps(data))
			print "F"
			result = json.loads(SockExt.recv_msg(s))
			enc_ct.b = EcPt.from_binary(binascii.unhexlify(result['return']),G)
			print "G"
			s.shutdown(socket.SHUT_RDWR)
			s.close()
			
			
		#Decrypt using the ephimeral private key
		print "H"
		value = enc_ct.dec(tmp_priv) #decrypt ct
		print "Z"
		return value
			
	except Exception as e:
		print "Exception during collective decryption: ", e
		return None

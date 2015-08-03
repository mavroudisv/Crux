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
	
	from numpy.random import laplace   
	
	proto = Classes.get_median(sk_sum, min_b = 0, max_b = 1000, steps = 20) #Compute Median
	plain = None
	total_noise = 0
	while True:
		v = proto.send(plain)
		if isinstance(v, int):
			break
		
		plain = collective_decryption(v, auths)
		
		if conf.DP:
			#print "sksum:" + str(sk_sum.epsilon)
			if sk_sum.epsilon != 0 and sk_sum.delta != 0:
				noise = 0
				scale = float(sk_sum.d) / float(sk_sum.epsilon)
				#print sk_sum.d
				#print sk_sum.epsilon
				noise = int(round(laplace(0, scale)))
				#print "noise: " + str(noise)
				plain += noise
				total_noise += noise
			
		#print "*: " + str(plain)

	#print "Estimated median: " + str(v)
	#print "Total Noise Added: " + str(total_noise)
	return str(v)


def mean_operation(elist, auths):
	
	G = EcGroup(nid=conf.EC_GROUP)
	esum = Classes.Ct.sum(elist)
	plain_sum = collective_decryption(esum, auths)
	
	mean = float(plain_sum)/float(len(elist))
	return str(mean)


def variance_operation(elist, elist_sq, auths):
	G = EcGroup(nid=conf.EC_GROUP)

	#E(x^2) = (S(ri^2)/N)
	plain_sum_sqs = list_sum_decryption(elist_sq, auths)
	#print "plain_sum_sqs: " + str(plain_sum_sqs)
	first = plain_sum_sqs/len(elist)
	
	#E(x)^2 = (S(ri)/N)^2
	esum = Classes.Ct.sum(elist)
	plain_sum = collective_decryption(esum, auths)
	tmp = float(plain_sum) / float(len(elist))
	second = tmp * tmp
	#print "second: " + str(second)

	variance = first - second
	return str(variance)



def mean_operation_streaming(sk_sum, auths):
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


def variance_operation_streaming(sk_sum, auths):    
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

#Break the list in smaller parts until the decryption is successful
def list_sum_decryption(elist, auths=[]):
	result = 0
	attempt = 0
	while result == 0:
		try:
			result = 0
			attempt += 1
			length = len(elist)
			part_size = len(elist)//attempt
			#print "Attempt: " + str(attempt)
			for i in range(length//part_size):
						
				_from = i * part_size
				if i < (length//part_size -1):
					_to = (i+1) * part_size
				else:
					_to = length
				
				esum_sqs = Classes.Ct.sum(elist[_from:_to])
				plain_part_sum = collective_decryption(esum_sqs, auths)
				result += plain_part_sum
			
		except Exception as e:
			#print " " + str(e)
			result = 0
			pass
	
	return result
	
def collective_decryption(ct, auths=[]):	
	try:
		#Generate ephimeral key
		G = EcGroup(nid=conf.EC_GROUP)
		tmp_priv = G.order().random()
		tmp_pub = tmp_priv * G.generator()

		#Encrypt with ephimeral key
		enc_ct = Classes.Ct.enc(tmp_pub, ct)
		
		for auth in auths: #Send for decryption to each authority
			json_obj_str = enc_ct.to_JSON()
			data = {'request':'partial_decrypt', 'contents': json_obj_str}
			#print data
			
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((auth, conf.AUTH_PORT)) #connect to authority
			SockExt.send_msg(s, json.dumps(data))

			result = json.loads(SockExt.recv_msg(s))
			enc_ct.b = EcPt.from_binary(binascii.unhexlify(result['return']),G)

			s.shutdown(socket.SHUT_RDWR)
			s.close()
			
			
		#Decrypt using the ephimeral private key
		value = enc_ct.dec(tmp_priv) #decrypt ct

		return value
			
	except Exception as e:
		#print "Exception during collective decryption: ", e
		return None

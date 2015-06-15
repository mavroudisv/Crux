import socket
import json
import time
from petlib.ec import *
import binascii
import sys

from includes import config as conf
from includes import utilities
from includes import Classes

G = EcGroup(nid=conf.EC_GROUP)

def remote_encrypt(ip, port, value):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, int(port)))
	data = {'request':'encrypt', 'contents': {'value':value}}
	s.sendall(json.dumps(data))
	result = json.loads(s.recv(1024))
	data = json.loads(result['return'])
	cipher_obj = Classes.Ct(EcPt.from_binary(binascii.unhexlify(data['pub']),G), EcPt.from_binary(binascii.unhexlify(data['a']),G), EcPt.from_binary(binascii.unhexlify(data['b']),G), Bn.from_hex(data['k']), None)
	s.close()
	return cipher_obj

def remote_decrypt(ip, port, cipher_obj):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, int(port)))
	json_obj_str = cipher_obj.to_JSON()
	data = {'request':'decrypt', 'contents': json_obj_str}
	s.sendall(json.dumps(data))
	result = json.loads(s.recv(1024))
	s.close()
	return result['return']
	
def main():	
	
	action = sys.argv[1]
	ip = sys.argv[2]
	port = sys.argv[3]


	if len(sys.argv)> 1 and sys.argv[1] == "ping":
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, int(port)))
		print utilities.ping(s)
		s.close()

	elif len(sys.argv)> 1 and sys.argv[1] == "pub":
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, int(port)))
		#pubkey
		data = {'request':'pubkey'}
		s.sendall(json.dumps(data))
		result = json.loads(s.recv(1024))
		print EcPt.from_binary(binascii.unhexlify(result['return']), G)
		s.close()

	elif len(sys.argv)> 1 and sys.argv[1] == "stat":
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, int(port)))
		data = {'request':'stat', 'contents': {'type':'median', 'attributes':{'file':'data/data_large.xls', 'sheet':'iadatasheet2', 'column_1':'Adults in Employment', 'column_2':'No adults in employment in household: With dependent children', 'column_3':'2011'}}}
		s.send(json.dumps(data))
		print "Request Sent"
		data = json.loads(s.recv(1024))
		print "Response:"
		result = data['return']
		
		if result['success']=='True':
			print "The %s of %s is: %s" %(result['type'] , result['attribute'], result['value'])
		else:
			print "Stat could not be computed."


	elif len(sys.argv)> 1 and sys.argv[1] == "encdec":

		value = 200
		tmp_obj = remote_encrypt(ip, port, value)
		new_value = remote_decrypt(ip, port, tmp_obj)
		print new_value
		assert value==new_value


	



if __name__ == "__main__":
	main()




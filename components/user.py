import socket
import json
import time
from petlib.ec import *
import binascii
import sys

from includes import utilities
from includes import Classes


def main():	
	
	G = EcGroup(nid=713)
	'''
	G = EcGroup(nid=713)
	g = G.hash_to_point(b"g")
	h = G.hash_to_point(b"h")
	o = G.order()
	priv = o.random()
	pub  = priv * g

	cipher_obj = Ct.enc(pub, 2)
	print cipher_obj.pub
	print (cipher_obj.to_JSON())
	data = cipher_obj.to_JSON()
	'''

	action = sys.argv[1]
	ip = sys.argv[2]
	port = sys.argv[3]
	

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, int(port)))

	if len(sys.argv)> 1 and sys.argv[1] == "ping":
		print utilities.ping(ip, int(port))

	elif len(sys.argv)> 1 and sys.argv[1] == "pub":

		#pubkey
		data = {'request':'pubkey'}
		s.send(json.dumps(data))
		result = json.loads(s.recv(1024))
		print EcPt.from_binary(binascii.unhexlify(result['return']), G)


	elif len(sys.argv)> 1 and sys.argv[1] == "encdec":


		#encrypt
		data = {'request':'encrypt', 'contents': {'value':200}}
		s.send(json.dumps(data))
		result = json.loads(s.recv(1024))
		data = json.loads(result['return'])
		from pprint import pprint
		pprint(data)
		 
		cipher_obj = Classes.Ct(EcPt.from_binary(binascii.unhexlify(data['pub']),G), EcPt.from_binary(binascii.unhexlify(data['a']),G), EcPt.from_binary(binascii.unhexlify(data['b']),G), Bn.from_hex(data['k']), None)
		pprint(cipher_obj.to_JSON())


		#decrypt
		json_obj_str = cipher_obj.to_JSON()
		data = {'request':'decrypt', 'contents': json_obj_str}
		#print data
		s.send(json.dumps(data))
		result = json.loads(s.recv(1024))
		print result['return']
		#from pprint import pprint
		#pprint(result)

		
	s.close()

	#s.send(json.dumps(data))
	#result = s.recv(1024)
	#h = hexlify(result).decode("utf8")
	#print EcPt.from_binary(result, G)

if __name__ == "__main__":
    main()

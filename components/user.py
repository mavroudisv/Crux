import socket
import json
import time
from petlib.ec import *
import binascii
import sys

from includes import config as conf
from includes import utilities
from includes import Classes


def main():	
	
	G = EcGroup(nid=conf.EC_GROUP)

	action = sys.argv[1]
	ip = sys.argv[2]
	port = sys.argv[3]
	

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(120.0)
	s.connect((ip, int(port)))

	if len(sys.argv)> 1 and sys.argv[1] == "ping":
		print utilities.ping(ip, int(port))

	elif len(sys.argv)> 1 and sys.argv[1] == "pub":

		#pubkey
		data = {'request':'pubkey'}
		s.send(json.dumps(data))
		result = json.loads(s.recv(1024))
		print EcPt.from_binary(binascii.unhexlify(result['return']), G)


	elif len(sys.argv)> 1 and sys.argv[1] == "stat":
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
		s.send(json.dumps(data))
		result = json.loads(s.recv(1024))
		print result['return']

	s.shutdown(socket.SHUT_RDWR)
	s.close()

if __name__ == "__main__":
	main()

import socket
import json
import time
from petlib.ec import *
import binascii
import sys
import numpy

from includes import config as conf
from includes import utilities
from includes import Classes
from includes import SocketExtend as SockExt
from includes import parser as p

#Globals
G = EcGroup(nid=conf.EC_GROUP)

def remote_encrypt(ip, port, value):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, int(port)))
	data = {'request':'encrypt', 'contents': {'value':value}}
	SockExt.send_msg(s, json.dumps(data))
	result = json.loads(SockExt.recv_msg(s))
	data = json.loads(result['return'])
	cipher_obj = Classes.Ct(EcPt.from_binary(binascii.unhexlify(data['pub']),G), EcPt.from_binary(binascii.unhexlify(data['a']),G), EcPt.from_binary(binascii.unhexlify(data['b']),G), Bn.from_hex(data['k']), None)
	s.close()
	return cipher_obj

def remote_decrypt(ip, port, cipher_obj):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, int(port)))
	json_obj_str = cipher_obj.to_JSON()
	data = {'request':'decrypt', 'contents': json_obj_str}
	SockExt.send_msg(s, json.dumps(data))
	result = json.loads(SockExt.recv_msg(s))
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
		SockExt.send_msg(s, json.dumps(data))
		result = json.loads(SockExt.recv_msg(s))
		print EcPt.from_binary(binascii.unhexlify(result['return']), G)
		s.close()

	elif len(sys.argv)> 1 and sys.argv[1] == "stat":
		tic = time.clock()
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, int(port)))
		#data = {'request':'stat', 'contents': {'type':'median', 'attributes':{'file':'data/data_large.xls', 'sheet':'iadatasheet2', 'column_1':'Adults in Employment', 'column_2':'No adults in employment in household: With dependent children', 'column_3':'2011'}}}
		data = {'request':'stat', 'contents': {'type':'median', 'attributes':{'file':'data/data_large.xls', 'sheet':'iadatasheet2', 'column_1':'Lone Parents', 'column_2':'Lone parents not in employment', 'column_3':'2011'}}}
		SockExt.send_msg(s, json.dumps(data))
		print "Request Sent"
		data = json.loads(SockExt.recv_msg(s))
		print "Response:"
		result = data['return']
		
		if result['success']=='True':
			approx_median = result['value']
			cor_median = comp_median('data/data_large.xls', 'iadatasheet2', 'Lone Parents', 'Lone parents not in employment', '2011')
			toc = time.clock()
			dt = (toc - tic)
			print "The %s of %s is: %s" %(result['type'] , result['attribute'], approx_median)
			print "The correct median is: " + str(cor_median)
			print "The err is: " + str(abs(approx_median - cor_median))
			print "Total time: " + str(dt)
			
		else:
			print "Stat could not be computed."


	elif len(sys.argv)> 1 and sys.argv[1] == "encdec":

		value = 200
		tmp_obj = remote_encrypt(ip, port, value)
		new_value = remote_decrypt(ip, port, tmp_obj)
		print new_value
		assert value==new_value



def comp_median(fn, sheet, column_1, column_2, column_3):
	#open xls
	rows = p.get_rows(fn, sheet, 1, 0) #determine which rows correspond to client
	values = p.read_xls_cell(fn, sheet, column_1, column_2, column_3, rows) #load values from xls
	median = numpy.median(values)
	
	#return median
	return median



if __name__ == "__main__":
	main()




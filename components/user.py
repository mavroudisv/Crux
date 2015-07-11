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
	

def comp_median(fn, sheet, column_1, column_2, column_3):
	rows = p.get_rows(fn, sheet, 1, 0) #determine which rows correspond to client
	values = p.read_xls_cell(fn, sheet, column_1, column_2, column_3, rows) #load values from xls
	median = numpy.median(values)
	return median

def comp_mean(fn, sheet, column_1, column_2, column_3):
	rows = p.get_rows(fn, sheet, 1, 0) #determine which rows correspond to client
	values = p.read_xls_cell(fn, sheet, column_1, column_2, column_3, rows) #load values from xls
	mean = numpy.mean(values)
	return mean

def comp_variance(fn, sheet, column_1, column_2, column_3):
	rows = p.get_rows(fn, sheet, 1, 0) #determine which rows correspond to client
	values = p.read_xls_cell(fn, sheet, column_1, column_2, column_3, rows) #load values from xls
	variance = numpy.var(values)
	return variance



if __name__ == "__main__":
		
	import argparse
	parser = argparse.ArgumentParser(description='User interface for privacy preserving statistics queries to the ToR network')
    
    #ip/port
	parser.add_argument('-s', '--server', type=str, help='Server name', required=True)
	parser.add_argument('-p', '--port', type=str, help='Port number', required=True, default='8888')
    
    #action
	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('--ping', action='store_true', help='Ping server')
	group.add_argument('--pub', action='store_true', help='Request the public key from authority')
	group.add_argument('--stat', help='Run size tests', nargs='+') #choices=['mean', 'median', 'variance']
	group.add_argument('--test', action='store_true', help='Verifies that the remote encryption and decryption work properly')
	
	args = parser.parse_args()
	
	
	#print comp_median('data/data_large.xls', 'iadatasheet2', 'Lone Parents', 'Lone parents not in employment', '2011')
	#print comp_variance('data/data_large.xls', 'iadatasheet2', 'Lone Parents', 'Lone parents not in employment', '2011')

	
	ip = args.server
	port = args.port
	

	if args.ping:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, int(port)))
		print utilities.ping(s)
		s.close()


	elif args.pub:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ip, int(port)))
		#pubkey
		data = {'request':'pubkey'}
		SockExt.send_msg(s, json.dumps(data))
		result = json.loads(SockExt.recv_msg(s))
		print EcPt.from_binary(binascii.unhexlify(result['return']), G)
		s.close()
		
	
	elif args.test:
		value = 12345
		tmp_obj = remote_encrypt(ip, port, value)
		new_value = remote_decrypt(ip, port, tmp_obj)
		print new_value
		if value==new_value:
			print "Test Successful!"
		else:
			print "Test failed."	

	elif args.stat:
		
		if args.stat[0] == 'mean':			
			tic = time.clock()
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, int(port)))
			#data = {'request':'stat', 'contents': {'type':'mean', 'attributes':{'file':'data/data_large.xls', 'sheet':'iadatasheet2', 'column_1':'Adults in Employment', 'column_2':'No adults in employment in household: With dependent children', 'column_3':'2011'}}}
			data = {'request':'stat', 'contents': {'type':'mean', 'attributes':{'file':'data/data_large.xls', 'sheet':'iadatasheet2', 'column_1':args.stat[1], 'column_2':args.stat[2], 'column_3':args.stat[3]}}}
			SockExt.send_msg(s, json.dumps(data))
			print "Request Sent"
			data = json.loads(SockExt.recv_msg(s))
			print "Response:"
			result = data['return']
			
			approx_res = result['value']
			cor_res = comp_mean('data/data_large.xls', 'iadatasheet2', args.stat[1], args.stat[2], args.stat[3])
			toc = time.clock()
			dt = (toc - tic)

		elif args.stat[0] == 'median':
			tic = time.clock()
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, int(port)))
			#data = {'request':'stat', 'contents': {'type':'median', 'attributes':{'file':'data/data_large.xls', 'sheet':'iadatasheet2', 'column_1':'Adults in Employment', 'column_2':'No adults in employment in household: With dependent children', 'column_3':'2011'}}}
			data = {'request':'stat', 'contents': {'type':'median', 'attributes':{'file':'data/data_large.xls', 'sheet':'iadatasheet2', 'column_1':args.stat[1], 'column_2':args.stat[2], 'column_3':args.stat[3]}}}
			SockExt.send_msg(s, json.dumps(data))
			print "Request Sent"
			data = json.loads(SockExt.recv_msg(s))
			print "Response:"
			result = data['return']
			
			approx_res = result['value']
			cor_res = comp_median('data/data_large.xls', 'iadatasheet2', args.stat[1], args.stat[2], args.stat[3])
			toc = time.clock()
			dt = (toc - tic)


		elif args.stat[0] == 'variance':
			tic = time.clock()
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((ip, int(port)))
			data = {'request':'stat', 'contents': {'type':'variance', 'attributes':{'file':'data/data_large.xls', 'sheet':'iadatasheet2', 'column_1':args.stat[1], 'column_2':args.stat[2], 'column_3':args.stat[3]}}}
			SockExt.send_msg(s, json.dumps(data))
			print "Request Sent"
			data = json.loads(SockExt.recv_msg(s))
			print "Response:"
			result = data['return']
			
			approx_res = result['value']
			cor_res = comp_variance('data/data_large.xls', 'iadatasheet2', args.stat[1], args.stat[2], args.stat[3])
			toc = time.clock()
			dt = (toc - tic)


		#Print stats results
		if result['success']=='True':
			print "The %s of %s is: %s" %(result['type'] , result['attribute'], approx_res)
			print "The correct result is: " + str(cor_res)
			print "The err is: " + str(abs(float(approx_res) - float(cor_res)))
			print "Total time: " + str(dt)
		else:
			print "Stat could not be computed."









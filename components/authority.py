from petlib.ec import *
import binascii

import SocketServer
import socket
import json
import time

from includes import config as conf
from includes import Classes
from includes import SocketExtend as SockExt

#Globals
G = EcGroup(nid=conf.EC_GROUP)
priv = None
pub = None

def listen_on_port(port):	
	server = TCPServer(('0.0.0.0', port), TCPServerHandler)
	server.serve_forever()


class TCPServer(SocketServer.ThreadingTCPServer):
	allow_reuse_address = True

class TCPServerHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		
		global G
		global priv
		global pub	

		try:
			inp = SockExt.recv_msg(self.request).strip()
			data = json.loads(inp)
			print "Request for: " + str(data['request'])
			
			if data['request'] == 'ping':
				contents = data['contents']
				SockExt.send_msg(self.request, json.dumps({'return': int(contents['value'])+1}))
			
			elif data['request'] == 'pubkey':
				SockExt.send_msg(self.request, json.dumps({'return': hexlify(pub.export())}))
				
			elif data['request'] == 'encrypt':
				contents = data['contents']
				cipher_obj = Classes.Ct.enc(pub, contents['value'])
				json_obj = cipher_obj.to_JSON()
				SockExt.send_msg(self.request, json.dumps({'return': json_obj}))
				
			elif data['request'] == 'decrypt':
				contents = json.loads(data['contents'])
				
				#from pprint import pprint
				#print "--------"
				#print(contents)
				
				try:
					new_k = Bn.from_hex(contents['k'])
				except:
					new_k = None
				
				#reconstruct object
				cipher_obj = Classes.Ct(
				EcPt.from_binary(binascii.unhexlify(contents['pub']),G),
				EcPt.from_binary(binascii.unhexlify(contents['a']),G),
				EcPt.from_binary(binascii.unhexlify(contents['b']),G),
				new_k, None)
				

				value = cipher_obj.dec(priv) #decrypt ct
				
				SockExt.send_msg(self.request, json.dumps({'return': value}))
			
			#self.request.shutdown(socket.SHUT_RDWR)
			#self.request.close()

			elif data['request'] == 'partial_decrypt':
				contents = json.loads(data['contents'])
				
				#from pprint import pprint
				#print "--------"
				#print(contents)
				
				try:
					new_k = Bn.from_hex(contents['k'])
				except:
					new_k = None
				
				#reconstruct object
				cipher_obj = Classes.Ct(
				EcPt.from_binary(binascii.unhexlify(contents['pub']),G),
				EcPt.from_binary(binascii.unhexlify(contents['a']),G),
				EcPt.from_binary(binascii.unhexlify(contents['b']),G),
				new_k, None)
				

				ct = cipher_obj.partial_dec(priv) #decrypt ct
				
				SockExt.send_msg(self.request, json.dumps({'return': hexlify(ct.export())}))
			
			#self.request.shutdown(socket.SHUT_RDWR)
			#self.request.close()			
			
					
		except Exception as e:		
			print "Exception on incomming connection: ", e

	

def load():		
	global G
	global priv
	global pub	

	print "Checking modules..."
	if (Classes.unit_tests()):
		print "Success! Loading..."
	else:
		print "Errors occurred. Aborting."
		return

	priv = G.order().random()
	pub= priv * G.generator()
	print "Generated public key is: " + str(pub)
	listen_on_port(conf.AUTH_PORT)	

if __name__ == "__main__":
    load()

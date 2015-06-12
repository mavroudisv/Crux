from petlib.ec import *
import binascii

import SocketServer
import json

from includes import config as conf
from includes import Classes

G = None
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
		
		while True:
			try:
				while True:
					inp = self.request.recv(1024).strip()
					if inp != '':
						break
				
				data = json.loads(inp)
				print data['request'] 
				# process the data, i.e. print it:
				
				if data['request'] == 'ping':
					contents = data['contents']
					self.request.sendall(json.dumps({'return': contents['value']}))
				
				elif data['request'] == 'pubkey':
					self.request.sendall(json.dumps({'return': hexlify(pub.export())}))
					
				elif data['request'] == 'encrypt':
					contents = data['contents']
					cipher_obj = Classes.Ct.enc(pub, contents['value'])
					json_obj = cipher_obj.to_JSON()
					self.request.sendall(json.dumps({'return': json_obj}))
					
				elif data['request'] == 'decrypt':
					contents = json.loads(data['contents'])

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
					
					self.request.sendall(json.dumps({'return': value}))

				else:
					break
						
			except Exception, e:		
				print "Exception: ", e


def load():		
	global G
	global priv
	global pub	
	G = EcGroup(nid=conf.EC_GROUP)
	priv = G.order().random()
	pub= priv * G.generator()
	print "Generated public key is: " + str(pub)
	listen_on_port(conf.AUTH_PORT)	

if __name__ == "__main__":
    load()

from petlib.ec import *
import binascii

import SocketServer
import json

from includes import Classes

G = None
priv = None
pub = None

def listen_on_port(port, pub, priv):

	print pub
	
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
					rec = self.request.recv(1024).strip()
					if rec != '':
						break
				
				data = json.loads(rec)
				print data['request'] 
				# process the data, i.e. print it:
				
				if data['request'] == 'ping':
					contents = data['contents']
					self.request.sendall(json.dumps({'return': contents['value']}))
				elif data['request'] == 'pubkey':
					self.request.sendall(json.dumps({'return': hexlify(pub.export())}))
					
				elif data['request'] == 'encrypt':

					
					#print data['contents']['value']
					contents = data['contents']
					cipher_obj = Classes.Ct.enc(pub, contents['value'])
					value = cipher_obj.dec(priv)					
					#print value
					#print contents['value']
					json_obj = cipher_obj.to_JSON()
					self.request.sendall(json.dumps({'return': json_obj}))
					#from pprint import pprint
					#pprint(json_obj)

					
				elif data['request'] == 'decrypt':
					G = EcGroup(nid=713)
					#contents = data['contents']
					contents = json.loads(data['contents'])
					#from pprint import pprint
					#pprint(contents)
					#create object
					#data = {'a':hexlify(self.a.export()), 'b':hexlify(self.b.export()), 'k':str(self.k.hex()), 'm':str(self.m), 'pub':hexlify(self.pub.export())}
					cipher_obj = Classes.Ct(EcPt.from_binary(binascii.unhexlify(contents['pub']),G), EcPt.from_binary(binascii.unhexlify(contents['a']),G), EcPt.from_binary(binascii.unhexlify(contents['b']),G), Bn.from_hex(contents['k']), None)
					#print cipher_obj.pub
					
					value = cipher_obj.dec(priv)					
					#print value

					#return plaintext
					self.request.sendall(json.dumps({'return': value}))
						
				else:
					break
						
			except Exception, e:
				
				print "Exception while receiving message: ", e


def load():		
	global G
	global priv
	global pub	
	G = EcGroup(nid=713)
	priv = G.order().random()
	pub= priv * G.generator()
	listen_on_port(8888, pub, priv)	

if __name__ == "__main__":
    load()

from petlib.ec import *
import binascii

import SocketServer
import json
import sys

from includes import utilities

G = None
priv = None
pub = None

supported_stats = ['median']
	
	
	
def listen_on_port(port, pub, priv):

	print pub
	
	server = TCPServer(('0.0.0.0', port), TCPServerHandler)
	server.serve_forever()


class TCPServer(SocketServer.ThreadingTCPServer):
	allow_reuse_address = True

class TCPServerHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		while True:
			try:
				data = json.loads(self.request.recv(1024).strip())
				print data['request'] 
				
				if data['request'] == 'ping':
					contents = data['contents']
					self.request.sendall(json.dumps({'return': contents['value']}))
				
				elif data['request'] == 'stat':
					contents = data['contents']
					
					stat_type = contents['type']
					attribute = contents['attribute']
					
					if contents['type'] in supported_stats:
						self.request.sendall(json.dumps({'return':{'success':'True', 'type':stat_type, 'attribute':attribute, 'value':200}}))
					else:						
						self.request.sendall(json.dumps({'return':{'success':'False', 'type':0, 'attribute':0, 'value': 0}}))
				
				else:
					break
						
			except Exception, e:
				pass
				#print "Exception while receiving message: ", e
	
	
	
		
def load():
	global G
	global priv
	global pub
	
	auths_str = sys.argv[1]
	auths = auths_str.split('-')
	
	G = EcGroup(nid=713)
	priv = G.order().random()
	pub = priv * G.generator()
	if utilities.multiping(8888, auths):
		listen_on_port(8888, pub, priv)	
	else:
		print "Not all authorities are responsive"

if __name__ == "__main__":
    load()

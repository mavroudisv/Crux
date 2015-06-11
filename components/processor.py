from petlib.ec import *
import binascii

import SocketServer
import json
import sys

from includes import utilities
from includes import Classes

G = None
priv = None
pub = None
auths = []
clients = []
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
					if contents['type'] in supported_stats:
						
						#read request
						#data = {'request':'stat', 'contents': {'type':'median', 'attributes':{'file':'', 'sheet':'', 'column_1':'', 'column_2':' ', 'column_3':''}}}
						
						
						
						contents = data['contents']
						stat_type = contents['type']
						attributes = contents['attributes']
						attr_file = attributes['file']
						attr_sheet = attributes['sheet']
						attr_column_1 = attributes['column_1']
						attr_column_2 = attributes['column_2']
						attr_column_3 = attributes['column_3']
						
						
						#send requests to clients, gather sketches
						for cl in clients:
							
						
							s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
							s.connect((cl, 8888))
							
							#add rows for each client
							data['contents']['attributes']['rows'] = ['E01000893', 'E01000895']
							s.send(json.dumps(data))
							json_obj = json.loads(s.recv(1024)) #store response
							s.close()


'''
							tmp_w = int(obj_json['vars']['w'])
							tmp_d = int(obj_json['vars']['d'])
							sketch = Classes.CountSketchCt(
							tmp_w, #w
							tmp_d, #d
							EcPt.from_binary(binascii.unhexlify(obj_json['vars']['pub']),G)) #pub

							#pprint(obj_json['store']['4']['a'])

							sketch.load_store_list(tmp_w, tmp_d, obj_json['store'])

							sketch.insert(11)
							c, d = sketch.estimate(11)
							est = c.dec(x)
							print est
						'''
						
					
						#add sketches
						
						#run stat protocol
					
						#return result
						self.request.sendall(json.dumps({'return':{'success':'True', 'type':'stat_type', 'attribute':'attribute', 'value':200}}))
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
	global auths
	global clients
	
	
	auths_str = sys.argv[1]
	clients_str = sys.argv[2]
	
	auths = auths_str.split('-')
	clients = clients_str.split('-')
	
	G = EcGroup(nid=713)
	priv = G.order().random()
	pub = priv * G.generator()
	if utilities.multiping(8888, auths):
		listen_on_port(8888, pub, priv)	
	else:
		print "Not all authorities are responsive"

if __name__ == "__main__":
    load()

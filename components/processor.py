from petlib.ec import *
import binascii

import SocketServer
import socket
import json
import sys
import math

from includes import config as conf
from includes import utilities
from includes import Classes

G = None
auths = []
clients = []
supported_stats = ['median']
	
	
	
def listen_on_port(port):
	
	server = TCPServer(('0.0.0.0', port), TCPServerHandler)
	server.serve_forever()


class TCPServer(SocketServer.ThreadingTCPServer):
	allow_reuse_address = True

class TCPServerHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		while True:
			try:
				data = json.loads(self.request.recv(1024).strip())
				print "Request for: " + str(data['request'])
				
				if data['request'] == 'ping':
					contents = data['contents']
					self.request.sendall(json.dumps({'return': contents['value']}))
				
				elif data['request'] == 'stat':
					
					contents = data['contents']
					try:
						contents = data['contents']
						stat_type = contents['type']
						attributes = contents['attributes']
						attr_file = attributes['file']
						attr_sheet = attributes['sheet']
						attr_column_1 = attributes['column_1']
						attr_column_2 = attributes['column_2']
						attr_column_3 = attributes['column_3']					
						
						#send requests to clients to gather sketches and add sketches
						sketches = []
						for cl in clients:
							sketch = get_sketch_from_client(cl, data)
							sketches.append(sketch)
							
						#Aggregate sketches
						sk_sum = Classes.CountSketchCt.aggregate(sketches)
						
						#Compute Median
						proto = Classes.get_median(sk_sum, min_b = 0, max_b = 1000, steps = 20)
						try:
							plain = None
							while True:
								v = proto.send(plain)
								if isinstance(v, int):
									break
								plain = collective_decrypt(v, auths)
								print "*: " + str(plain)

							print("Estimated median: %s" % (v))
						except Exception as e:						
							print e
						c, d = sk_sum.estimate(9.0)
						est = collective_decrypt(c, auths)

											
						self.request.sendall(json.dumps({'return':{'success':'True', 'type':stat_type, 'attribute':attr_column_1, 'value':est}}))
					
					except Exception as e:						
						self.request.sendall(json.dumps({'return':{'success':'False', 'type':0, 'attribute':0, 'value': e}}))
				
				else:
					break
						
			except Exception, e:
				pass
				#print "Exception while receiving message: ", e
	

def get_sketch_from_client(client_ip, data):
	try:
		data['contents']['attributes']['rows'] = ['E01000893', 'E01000895']
		#data['contents']['attributes']['rows'] = ['E01000893']
			
		tmp_w = int(math.ceil(math.e / conf.EPSILON))
		tmp_d = int(math.ceil(math.log(1.0 / conf.DELTA)))
		print tmp_w
		print tmp_d
		
		data['contents']['attributes']['sk_w'] = tmp_w
		data['contents']['attributes']['sk_d'] = tmp_d
		
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((client_ip, conf.CLIENT_PORT))												
		s.send(json.dumps(data))
		obj_json = json.loads(s.recv(100000000)) #store response
		s.close()
		
		
		data = json.loads(obj_json['return'])
		tmp_w = int(data['vars']['w'])
		tmp_d = int(data['vars']['d'])
		
		
		sketch = Classes.CountSketchCt(tmp_w, tmp_d, EcPt.from_binary(binascii.unhexlify(data['vars']['pub']),G))
		sketch.load_store_list(tmp_w, tmp_d, data['store'])


		return sketch
	except Exception, e:
		print "Exception while getting sketch from client: ", e


	
def collective_decrypt(ct, auths=[]):
	for auth in auths:
		try:
			
			json_obj_str = ct.to_JSON()
			data = {'request':'decrypt', 'contents': json_obj_str}

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((auth, conf.AUTH_PORT)) #connect to authority
			s.send(json.dumps(data))
			
			result = json.loads(s.recv(1024))
			s.close()

			return result['return']
			
		except Exception as e:
			print "Exception in collective decrypt: ", e
			return None


		
def load():
	global G
	global auths
	global clients
	
	
	G = EcGroup(nid=conf.EC_GROUP)
	
	auths_str = sys.argv[1]
	clients_str = sys.argv[2]
	auths = auths_str.split('-')
	clients = clients_str.split('-')
	
    
	if utilities.multiping(conf.AUTH_PORT, auths):
		print "Authorities responsive. Listening..."
		listen_on_port(conf.PROCESSOR_PORT)	
	else:
		print "Not all authorities are responsive."

if __name__ == "__main__":
    load()

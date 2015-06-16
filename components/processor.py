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
from includes import SocketExtend as SockExt

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
		try:
			data = json.loads(self.request.recv(1024).strip())
			print "Request for: " + str(data['request'])
			
			if data['request'] == 'ping':
				contents = data['contents']
				self.request.sendall(json.dumps({'return': contents['value']}))
			
			elif data['request'] == 'stat':
				
				contents = data['contents']
				stat_type = contents['type']
				
				attributes = contents['attributes']
				attr_file = attributes['file']
				attr_sheet = attributes['sheet']
				attr_column_1 = attributes['column_1']
				attr_column_2 = attributes['column_2']
				attr_column_3 = attributes['column_3']					
				
				#Send requests to clients to gather sketches and add sketches
				sketches = []
				for cl in clients:
					sketch = get_sketch_from_client(cl, data)
					sketches.append(sketch)
					
				
				sk_sum = Classes.CountSketchCt.aggregate(sketches) #Aggregate sketches
				
				#Run selected operation
				if (stat_type == 'median'):
					median = median_operation(sk_sum) #Compute median on sum of sketches
					self.request.sendall(json.dumps({'return':{'success':'True', 'type':stat_type, 'attribute':attr_column_1, 'value':median}}))
					print 'Stat computed. Listening for requests...'
				else:
					self.request.sendall(json.dumps({'return':{'success':'False', 'Reason': 'Stat type not supported.'}}))
				
				
		except Exception as e:						
			print 'Exception on incomming connection: ' + str(e)				
			
			
def median_operation(sk_sum):
	proto = Classes.get_median(sk_sum, min_b = 0, max_b = 1000, steps = 20) #Compute Median
	plain = None
	while True:
		v = proto.send(plain)
		if isinstance(v, int):
			break
		plain = collective_decryption(v, auths)
		#print "*: " + str(plain)

	#print "Estimated median: " + str(v)
	return str(v)

def get_sketch_from_client(client_ip, data):
	try:
					
		#Compute sketch parameters
		tmp_w = int(math.ceil(math.e / conf.EPSILON))
		tmp_d = int(math.ceil(math.log(1.0 / conf.DELTA)))

		data['contents']['attributes']['sk_w'] = tmp_w
		data['contents']['attributes']['sk_d'] = tmp_d
		
		#Fetch data from client as a serialized sketch object
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((client_ip, conf.CLIENT_PORT))												
		s.send(json.dumps(data))
		#data = s.recv(100000000)
		data = SockExt.recv_msg(s)
		#print data
		obj_json = json.loads(data) #The sketch object can be quite large
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		
		
		data = json.loads(obj_json['return'])
		#tmp_w = int(data['vars']['w'])
		#tmp_d = int(data['vars']['d'])
		
		 #De-serialize sketch object
		sketch = Classes.CountSketchCt(tmp_w, tmp_d, EcPt.from_binary(binascii.unhexlify(data['vars']['pub']),G))
		sketch.load_store_list(tmp_w, tmp_d, data['store'])

		return sketch

	except Exception, e:
		print "Exception while getting sketch from client: ", e


	
def collective_decryption(ct, auths=[]):
	for auth in auths:
		try:
			
			json_obj_str = ct.to_JSON()
			data = {'request':'decrypt', 'contents': json_obj_str}

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((auth, conf.AUTH_PORT)) #connect to authority
			s.send(json.dumps(data))
			
			result = json.loads(s.recv(1024))
			s.shutdown(socket.SHUT_RDWR)
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

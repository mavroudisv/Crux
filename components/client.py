import socket
import json
import sys
from petlib.ec import EcGroup, EcPt
from petlib.bn import Bn
import binascii
import SocketServer
import json
import csv
import time
import xlrd
from itertools import product

from includes import config as conf
from includes import utilities
from includes import parser as p
from includes import Classes
from includes import SocketExtend as SockExt

#Globals
G = EcGroup(nid=conf.EC_GROUP)
auths=[]
common_key = None
data_dict = None
unique_id = None
num_clients = None


def listen_on_port(port):
	server = TCPServer(('0.0.0.0', port), TCPServerHandler)
	server.serve_forever()


class TCPServer(SocketServer.ThreadingTCPServer):
	allow_reuse_address = True


class TCPServerHandler(SocketServer.BaseRequestHandler):
	def handle_clean(self):
		global G
		global priv
		global pub
		global auths
		global common_key
		
		try:
			inp = SockExt.recv_msg(self.request).strip()				
			data = json.loads(inp)
			print "Request for: " + str(data['request'])

			if data['request'] == 'stat':
				#print data['contents']
				#parameters
				contents = data['contents']
				stat_type = contents['type']
				attributes = contents['attributes']
				attr_file = attributes['file']
				attr_sheet = attributes['sheet']
				attr_column_1 = attributes['column_1']
				attr_column_2 = attributes['column_2']
				attr_column_3 = attributes['column_3']
				sk_w = attributes['sk_w']
				sk_d = attributes['sk_d']
			
				print "A"
				rows = p.get_rows(attr_file,attr_sheet, num_clients, unique_id) #determine which rows correspond to client
				print "B"
				values = p.read_xls_cell(attr_file, attr_sheet, attr_column_1, attr_column_2, attr_column_3, rows) #load values from xls
				print "C"
				plain_sketch = generate_sketch(int(sk_w), int(sk_d), values) #construct sketch from values
				print "D"
				SockExt.send_msg(self.request, json.dumps({'return': plain_sketch.to_JSON()})) #return serialized sketch
				print "Request served."
				
				if conf.MEASUREMENT_MODE_CLIENT:
					self.server.shutdown()
			else:
				print "Unknown request type."
				
					
		except Exception as e:
			print "Exception on incomming connection: ", e
	
	
	def handle(self):
		if conf.MEASUREMENT_MODE_CLIENT:
	
			if conf.PROFILER == 'cProfiler':
				import cProfile
				import pstats
				pr = cProfile.Profile()
				pr.enable()
				self.handle_clean()
				pr.disable()
				
				#pr.dump_stats(conf.PROF_FILE_CLIENT + "pickle") #pickled
				
				#readable
				sortby = 'cumulative'
				ps = pstats.Stats(pr, stream=open(conf.PROF_FILE_CLIENT + "prof", 'w')).sort_stats(sortby)
				ps.print_stats()
				
				
			elif conf.PROFILER == 'LineProfiler':
				import line_profiler
				import pstats
				import io
				pr = line_profiler.LineProfiler(self.handle_clean, get_sketches_from_clients_non_blocking
					, Classes.CountSketchCt.aggregate, op.median_operation, op.mean_operation, op.variance_operation)
				pr.enable()
				self.handle_clean()
				pr.disable()
				
				pr.print_stats(open(conf.PROF_FILE_CLIENT + "prof", 'w')) #readable
				#pr.dump_stats(conf.PROF_FILE_CLIENT + "pickle") #pickled

	
			elif conf.PROFILER == "viz":
				from pycallgraph import PyCallGraph
				from pycallgraph.output import GraphvizOutput
				from pycallgraph import Config
				DEPTH = 3
				config = Config(max_depth=DEPTH)
				graphviz = GraphvizOutput()
				graphviz.output_file = conf.PROF_FILE_CLIENT + 'png'
				with PyCallGraph(output=graphviz, config=config):
					self.handle_clean()


			else:
				self.handle_clean()

		else:
			self.handle_clean()
		
	


#Add values to sketch
def generate_sketch(w, d, values=[]):
	
	sk = Classes.CountSketchCt(w, d, common_key)
	for v in values:
		sk.insert(int(v))	
	
	return sk


#Compute the group public key
def generate_group_key(auths=[]):
	pub_keys = []
	for auth_ip in auths: #get pub key from each auth
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#s.settimeout(10.0)
		s.connect((auth_ip, conf.AUTH_PORT))
		data = {'request':'pubkey'}
		SockExt.send_msg(s, json.dumps(data))
		result = json.loads(SockExt.recv_msg(s))
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		
		new_key = EcPt.from_binary(binascii.unhexlify(result['return']), G) #De-serialize Ecpt object
		pub_keys.append(new_key)
	
	#Add keys
	c_pub = pub_keys[0]
	print c_pub
	for pkey in pub_keys[1:]:
		print pkey
		c_pub += pkey #pub is ecpt, so we add
	return c_pub


def load():
	global G
	global auths
	global common_key
	global unique_id
	global num_clients
	
	auths_str = sys.argv[1]
	processors_str = sys.argv[2]
	
	unique_id = int(sys.argv[3])
	print "Client id: " + str(unique_id)
	num_clients = int(sys.argv[4])

	
	auths = auths_str.split('-')
	processors = processors_str.split('-')
	
	#Make sure all components are up
	all_responsive = True
	if utilities.alive(conf.AUTH_PORT, auths):
		print "All authorities are responsive"
	else:
		all_responsive = False
		print "Not all authorities are responsive"

	if utilities.alive(conf.PROCESSOR_PORT, processors):
		print "Processor is responsive."
	else:
		all_responsive = False
		print "Processor is not responsive."
	
	
	if all_responsive == True: #if all components up
		common_key = generate_group_key(auths) #compute common key
		print "Common key: " + str(common_key)
		print "Listening for requests..."
		listen_on_port(conf.CLIENT_PORT) #listen for requests




if __name__ == "__main__":
    load()
    


from petlib.ec import *
import binascii

import SocketServer
import socket
import json
import sys
import math
import sys
import traceback
import sys


from includes import config as conf
from includes import utilities
from includes import Classes
from includes import SocketExtend as SockExt
from includes import operations as op


#Globals
G = EcGroup(nid=conf.EC_GROUP)
auths = []
clients = []
supported_stats = ['median']
	
	

def listen_on_port(port):
	server = TCPServer(('0.0.0.0', port), TCPServerHandler)
	server.serve_forever()


class TCPServer(SocketServer.ThreadingTCPServer):
	allow_reuse_address = True

class TCPServerHandler(SocketServer.BaseRequestHandler):
	
	def handle_clean(self):
		try:
			data = json.loads(SockExt.recv_msg(self.request).strip())
			print "Request for: " + str(data['request'])
			
			if data['request'] == 'ping':
				contents = data['contents']
				SockExt.send_msg(self.request, json.dumps({'return': contents['value']}))
			
			elif data['request'] == 'stat':
				process_request(data, self)


		except Exception as e:						
			SockExt.send_msg(self.request, json.dumps({'return':{'success':'False'}}))
			print 'Exception on incoming connection: ' + str(e)
				
				
	def handle(self):
		if conf.MEASUREMENT_MODE_PROCESSOR:
			
			if conf.PROFILER == 'cProfiler':
				import cProfile
				import pstats
				pr = cProfile.Profile()
				pr.enable()
				self.handle_clean()
				pr.disable()
				
				#pr.dump_stats(conf.PROF_FILE_PROCESSOR + "pickle") #pickled
				
				#readable
				sortby = 'cumulative'
				ps = pstats.Stats(pr, stream=open(conf.PROF_FILE_PROCESSOR + "prof", 'w')).sort_stats(sortby)
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
				
				pr.print_stats(open(conf.PROF_FILE_PROCESSOR + "prof", 'w')) #readable
				#pr.dump_stats(conf.PROF_FILE_PROCESSOR + "pickle") #pickled

	
			elif conf.PROFILER == "viz":
				from pycallgraph import PyCallGraph
				from pycallgraph.output import GraphvizOutput
				from pycallgraph import Config
				DEPTH = 3
				config = Config(max_depth=DEPTH)
				graphviz = GraphvizOutput()
				graphviz.output_file = conf.PROF_FILE_PROCESSOR + 'png'
				with PyCallGraph(output=graphviz, config=config):
					self.handle_clean()

			else:
				self.handle_clean()
				
		else:
			self.handle_clean()		



def process_request(data, obj):
	#parameters
	contents = data['contents']
	stat_type = contents['type']
	attributes = contents['attributes']
	attr_file = attributes['file']
	attr_sheet = attributes['sheet']
	attr_column_1 = attributes['column_1']
	attr_column_2 = attributes['column_2']
	attr_column_3 = attributes['column_3']
	
	
	#Run selected operation
	if (stat_type == 'median'):
		sketches = get_sketches_from_clients_non_blocking(clients, data) #Gather sketches from clients
		sk_sum = Classes.CountSketchCt.aggregate(sketches) #Aggregate sketches
		result = op.median_operation(sk_sum, auths) #Compute median on sum of sketches

	elif (stat_type == 'mean'):
		print "A"
		value_sets = get_values_from_clients_non_blocking(clients, data) #Gather sketches from clients
		
		elist = []
		for vset in value_sets:
			for value in vset:
				elist.append(value)
		
		result = op.mean_operation(elist, auths) #Compute mean from cts
		
	elif (stat_type == 'variance'):
		values = get_values_from_clients_non_blocking(clients, data) #Gather sketches from clients
		result = op.variance_operation(values, auths) #Compute mean from cts
		
		
	SockExt.send_msg(obj.request, json.dumps({'return':{'success':'True', 'type':stat_type, 'attribute':attr_column_1, 'value':result}}))
	
	print 'Stat computed. Listening for requests...'
	
	if conf.MEASUREMENT_MODE_PROCESSOR:
		obj.server.shutdown()


def get_values_from_clients_non_blocking(client_ips, data):
	try:			
		import select
		import socket
		import sys
		import Queue

		inputs = []
		outputs = []

		#Prepare sockets
		value_sets = []
		for cl_ip in client_ips:
			#Fetch data from client as a serialized sketch object
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
			#print >>sys.stderr, 'starting up on %s port %s' % (cl_ip, conf.CLIENT_PORT)
			s.connect((cl_ip, conf.CLIENT_PORT))
			#s.listen(5) # Listen for incoming connections
			outputs.append(s)

		print "D"
		# Outgoing message queues (socket:Queue)
		#message_queues = {}

		while inputs or outputs:

			# Wait for at least one of the sockets to be ready for processing
			#print >>sys.stderr, '\nwaiting for the next event'
			readable, writable, exceptional = select.select(inputs, outputs, inputs)

			#Handle outputs
			for s in writable:
				SockExt.send_msg(s, json.dumps(data))
				inputs.append(s)
				outputs.remove(s)

			# Handle inputs
			for s in readable:
				data = SockExt.recv_msg(s)
				#print data
				inputs.remove(s)
				s.shutdown(socket.SHUT_RDWR)
				s.close()

				print "D2"
				obj_json = json.loads(data)
				print "D3"
				#print obj_json['return']
				contents = obj_json['return']
				print "D4"
				print "E"
				values = load_value_set(contents['store'])
				print "F"
				value_sets.append(values)
				
		
		

		return value_sets

	except Exception as e:
		print "Exception while getting value from client: " + str(e)
		traceback.print_exc()




def load_value_set(cont_dict):	
	ct_values = []	
	counter = 0
	print "C"
	for i in range(len(cont_dict)):              
		contents = cont_dict[str(i)]                        
		ct_values.append(Classes.Ct(EcPt.from_binary(binascii.unhexlify(contents['pub']),G), EcPt.from_binary(binascii.unhexlify(contents['a']),G), EcPt.from_binary(binascii.unhexlify(contents['b']),G), Bn.from_hex(contents['k']), Bn.from_hex(contents['m'])))
		
	
	return ct_values



def get_sketches_from_clients_non_blocking(client_ips, data):
	try:			
		#Compute sketch parameters
		tmp_w = int(math.ceil(math.e / conf.EPSILON))
		tmp_d = int(math.ceil(math.log(1.0 / conf.DELTA)))

		data['contents']['attributes']['sk_w'] = tmp_w
		data['contents']['attributes']['sk_d'] = tmp_d

		import select
		import socket
		import sys
		import Queue

		inputs = []
		outputs = []

		#Prepare sockets
		sketches = []
		for cl_ip in client_ips:
			#Fetch data from client as a serialized sketch object
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
			#print >>sys.stderr, 'starting up on %s port %s' % (cl_ip, conf.CLIENT_PORT)
			s.connect((cl_ip, conf.CLIENT_PORT))
			#s.listen(5) # Listen for incoming connections
			outputs.append(s)


		# Outgoing message queues (socket:Queue)
		#message_queues = {}

		while inputs or outputs:

			# Wait for at least one of the sockets to be ready for processing
			#print >>sys.stderr, '\nwaiting for the next event'
			readable, writable, exceptional = select.select(inputs, outputs, inputs)

			#Handle outputs
			for s in writable:
				SockExt.send_msg(s, json.dumps(data))
				inputs.append(s)
				outputs.remove(s)


			# Handle inputs
			for s in readable:
				data = SockExt.recv_msg(s)
				#print data
				inputs.remove(s)
				s.shutdown(socket.SHUT_RDWR)
				s.close()

				obj_json = json.loads(data)
				contents = json.loads(obj_json['return'])
				#tmp_w = int(data['vars']['w'])
				#tmp_d = int(data['vars']['d'])
				
				#De-serialize sketch object
				sketch = Classes.CountSketchCt(tmp_w, tmp_d, EcPt.from_binary(binascii.unhexlify(contents['vars']['pub']),G))
				sketch.load_store_list(tmp_w, tmp_d, contents['store'])
				sketches.append(sketch)
				
		############# NON-BLOCKING PART #############

		return sketches

	except Exception as e:
		print "Exception while getting sketch from client: " + str(e)
		traceback.print_exc()



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
		SockExt.send_msg(s, json.dumps(data))

		data = SockExt.recv_msg(s)

		obj_json = json.loads(data) #The sketch object can be quite large
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		
		contents = json.loads(obj_json['return'])
		#tmp_w = int(data['vars']['w'])
		#tmp_d = int(data['vars']['d'])
		
		#De-serialize sketch object
		sketch = Classes.CountSketchCt(tmp_w, tmp_d, EcPt.from_binary(binascii.unhexlify(contents['vars']['pub']),G))
		sketch.load_store_list(tmp_w, tmp_d, contents['store'])

		return sketch

	except Exception as e:
		print "Exception while getting sketch from client: " + str(e)
		traceback.print_exc()


		
def load():
	global G
	global auths
	global clients
	
	auths_str = sys.argv[1]
	clients_str = sys.argv[2]
	auths = auths_str.split('-')
	clients = clients_str.split('-')
    
    
    #profiler = sys.argv[3]
	from pycallgraph import PyCallGraph
	from pycallgraph.output import GraphvizOutput
	
	if utilities.alive(conf.AUTH_PORT, auths):
		print "Authorities responsive. Listening..."
		listen_on_port(conf.PROCESSOR_PORT)
	else:
		print "Not all authorities are responsive."
	

if __name__ == "__main__":
    load()

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
import gc

from includes import config as conf
from includes import utilities
from includes import Classes
from includes import SocketExtend as SockExt


G = None
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
	def handle(self):
		
		global G
		global priv
		global pub
		global auths
		global common_key
		
		try:
			inp = self.request.recv(1024).strip()				
			data = json.loads(inp)
			print "Request for: " + str(data['request'])

			if data['request'] == 'stat':
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
			
				#rows = attributes['rows']
				#rows = ['E01000889', 'E01000890', 'E01000891'] #IT WORKS!
	
				#CRASHES WHEN READING INPUT FROM CLIENT. POSSIBLY VERY LARGE INPUT
				#rows = ['E01000907', 'E01000908', 'E01000909', 'E01000912', 'E01000913', 'E01000893', 'E01000894']
				#data['contents']['attributes']['rows'] = ['E01000893']
				
				num_rows = count_rows(attr_file, attr_sheet)
				(lower, upper) = give_range(int(num_clients), int(num_rows), 3, unique_id, (unique_id == num_clients-1))
				values = read_xls_cell(attr_file, attr_sheet, attr_column_1, attr_column_2, attr_column_3, int(lower), int(upper))
				#values = read_xls_cell('data/data_large.xls','iadatasheet2','Adults in Employment', 'No adults in employment in household: With dependent children','2011',rows)
				
				plain_sketch = generate_sketch(int(sk_w), int(sk_d), values) #construct sketch
				
				#print json.dumps({'return': plain_sketch.to_JSON()})
				
				
				#self.request.sendall(json.dumps({'return': plain_sketch.to_JSON()})) #return serialized sketch
				
				SockExt.send_msg(self.request, json.dumps({'return': plain_sketch.to_JSON()})) #return serialized sketch
				values = []
				plain_sketch = None
				gc.collect()
				
					
		except Exception, e:
			print "Exception on incomming connection: ", e


def count_rows(filename, sheet):

	workbook = xlrd.open_workbook(filename)
	worksheet = workbook.sheet_by_name(sheet)
	return worksheet.nrows


def give_range(num_clients, num_rows, num_labels_rows, client_id, add_residual=False):
	
	num_clean_rows = num_rows - num_labels_rows
	rows_per_client = num_clean_rows / num_clients
	
	_from = rows_per_client*client_id + num_labels_rows + 1
	_to = rows_per_client*(client_id+1) + num_labels_rows
	
	#add residual in the first client
	if add_residual:
		residual = num_clean_rows - (rows_per_client * num_clients)
		_to += residual

	return (_from, _to)

#Fetch from the xls cells with matching labels
def read_xls_cell(filename, sheet, column_lbl_1, column_lbl_2, column_lbl_3, lower_bound, upper_bound):
	
	cells = []
	
	workbook = xlrd.open_workbook(filename)
	worksheet = workbook.sheet_by_name(sheet)
	

	from itertools import product
	for row_index in xrange(worksheet.nrows):
		for col_index in xrange(worksheet.ncols):

			#row label
			tmp_row_lbl = worksheet.cell(row_index, 0).value

			#column label 1
			tmp_counter = col_index
			tmp_label = ''
			while True:
				tmp_label = worksheet.cell(0, tmp_counter).value
				if tmp_label != '':
					break
				tmp_counter -= 1

			tmp_col_lbl_1 = tmp_label

			#column label 2
			tmp_counter = col_index
			tmp_label = ''
			while True:
				tmp_label = worksheet.cell(1, tmp_counter).value
				if tmp_label != '':
					break
				tmp_counter -= 1
			
			tmp_col_lbl_2 = tmp_label
			
			#column label 3
			tmp_counter = col_index
			tmp_label = ''
			while True:
				tmp_label = worksheet.cell(2, tmp_counter).value
				if tmp_label != '':
					break
				tmp_counter -= 1
		
			#excel treats every num as float and adds .0
			if isinstance(tmp_label, float):
				tmp_col_lbl_3 = str(tmp_label)[:-2]
			else:
				tmp_col_lbl_3 = tmp_label

		
			#print tmp_col_lbl_1,tmp_col_lbl_2,tmp_col_lbl_3,tmp_row_lbl
			if (tmp_col_lbl_1 == column_lbl_1
			 and tmp_col_lbl_2 == column_lbl_2
			 and tmp_col_lbl_3 == column_lbl_3
			 and row_index<=upper_bound
			 and row_index>=lower_bound):
				cells.append(worksheet.cell(row_index, col_index).value) #add cell to list
				print worksheet.cell(row_index, col_index).value

	return cells

#Add values to sketch
def generate_sketch(w, d, values=[]):
	sk = Classes.CountSketchCt(w, d, common_key)
	for v in values:
		#print type(v)
		sk.insert(int(v))	
	return sk


#Compute the group public key
def generate_group_key(auths=[]):
	pub_keys = []
	for auth_ip in auths: #get pub key from each auth
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(10.0)
		s.connect((auth_ip, conf.AUTH_PORT))
		data = {'request':'pubkey'}
		s.send(json.dumps(data))
		result = json.loads(s.recv(1024))
		s.shutdown(socket.SHUT_RDWR)
		s.close()
		
		new_key = EcPt.from_binary(binascii.unhexlify(result['return']), G) #De-serialize Ecpt object
		pub_keys.append(new_key)
	
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
	unique_id = sys.argv[3]
	print unique_id
	num_clients = sys.argv[4]
	print num_clients
	
	auths = auths_str.split('-')
	processors = processors_str.split('-')
	
	#Make sure all components are up
	all_responsive = True
	if utilities.multiping(conf.AUTH_PORT, auths):
		print "All authorities are responsive"
	else:
		all_responsive = False
		print "Not all authorities are responsive"

	if utilities.multiping(conf.PROCESSOR_PORT, processors):
		print "Processor is responsive."
	else:
		all_responsive = False
		print "Processor is not responsive."
	
	
	if all_responsive == True: #if all components up
		G = EcGroup(nid=conf.EC_GROUP)
		common_key = generate_group_key(auths) #compute common key
		print "Common key: " + str(common_key)
		print "Listening for requests..."
		listen_on_port(conf.CLIENT_PORT) #listen for requests




if __name__ == "__main__":
    load()
    


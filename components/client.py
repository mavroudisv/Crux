import socket
import json
import sys
from petlib.ec import EcGroup, EcPt
from petlib.bn import Bn
import binascii
import SocketServer
import json
import csv

from includes import config as conf
from includes import utilities
from includes import Classes

G = None
auths=[]
common_key = None
data_dict = None



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
		
		while True:
			try:
				while True:
					inp = self.request.recv(1024).strip()
					if inp != '':
						break
				
				data = json.loads(inp)
				print data['request']

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
					rows = attributes['rows']
					sk_w = attributes['sk_w']
					sk_d = attributes['sk_d']
					
					#load values from xls
					values = read_xls_cell('data/data_large.xls','iadatasheet2','Adults in Employment', 'No adults in employment in household: With dependent children','2011',rows)
					
					plain_sketch = generate_sketch(int(sk_w), int(sk_d), values) #construct sketch
					
					self.request.sendall(json.dumps({'return': plain_sketch.to_JSON()})) #return serialized sketch
					
				else:
					break
						
			except Exception, e:
				
				print "Exception while receiving message: ", e



#Fetch from the xls cells with matching labels
def read_xls_cell(filename, sheet, column_lbl_1, column_lbl_2, column_lbl_3, row_lbls=[]):
	
	cells = []
	
	import xlrd
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
			 and tmp_row_lbl in row_lbls): #if (row and columns labels) match was found
				 cells.append(worksheet.cell(row_index, col_index).value) #add cell to list
		
	return cells


#Add values to sketch
def generate_sketch(w, d, values=[]):
	sk = Classes.CountSketchCt(w, d, common_key)
	for v in values:
		sk.insert(v)	
	return sk


#Compute the group public key
def generate_group_key(auths=[]):
	pub_keys = []
	for auth_ip in auths: #get pub key from each auth
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((auth_ip, conf.AUTH_PORT))
		data = {'request':'pubkey'}
		s.send(json.dumps(data))
		result = json.loads(s.recv(1024))
		s.close()
		new_key = EcPt.from_binary(binascii.unhexlify(result['return']), G)
		pub_keys.append(new_key)
	
	c_pub = pub_keys[0]

	for pkey in pub_keys[1:]:
		print pkey_key
		c_pub += pkey #pub is ecpt, so we add
   
	return c_pub


def load():
	global G
	global auths
	global common_key

	
	auths_str = sys.argv[1]
	processors_str = sys.argv[2]
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
    


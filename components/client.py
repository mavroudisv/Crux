import socket
import json
import sys
from petlib.ec import EcGroup, EcPt
from petlib.bn import Bn
import binascii
import SocketServer
import json
import csv

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
					rec = self.request.recv(1024).strip()
					if rec != '':
						break
				
				data = json.loads(rec)
				print data['request'] 
				# process the data, i.e. print it:
				
					
				if data['request'] == 'sketch':
					
					
					#{'request':'stat', 'contents': {'type':'median', 'attributes':{'file':'', 'sheet':'', 'column_1':'', 'column_2':' ', 'column_3':''}}}
					contents = data['contents']
					stat_type = contents['type']
					attributes = contents['attributes']
					attr_file = attributes['file']
					attr_sheet = attributes['sheet']
					attr_column_1 = attributes['column_1']
					attr_column_2 = attributes['column_2']
					attr_column_3 = attributes['column_3']
					rows = attributes['rows']
					
					#rows = []
					#rows.append('E01000893')
					#rows.append('E01000895')
					
					#load json
					#replace string consts with json strings
					values = read_xls_cell('data/data_large.xls','iadatasheet2','Adults in Employment', 'No adults in employment in household: With dependent children','2011',rows)
					plain_sketch = generate_sketch(values)
					encrypt_sketch(plain_sketch, common_key)
					
					contents = json.loads(data['contents'])
					cipher_obj = Classes.Ct(EcPt.from_binary(binascii.unhexlify(contents['pub']),G), EcPt.from_binary(binascii.unhexlify(contents['a']),G), EcPt.from_binary(binascii.unhexlify(contents['b']),G), Bn.from_hex(contents['k']), None)
					value = cipher_obj.dec(priv)					
					self.request.sendall(json.dumps({'return': value}))
						
				else:
					break
						
			except Exception, e:
				
				print "Exception while receiving message: ", e





#num of rows can in our case be determined by the processor
def read_xls_cell(filename, sheet, column_lbl_1, column_lbl_2, column_lbl_3, row_lbls=[]): #column attribute of stat
	
	cells = []
	
	import xlrd
	workbook = xlrd.open_workbook(filename)
	worksheet = workbook.sheet_by_name(sheet)
	

	from itertools import product
	for row_index in xrange(worksheet.nrows):
		for col_index in xrange(worksheet.ncols):

			#print col_index
			#print row_index
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
			#print '------------'
			if (tmp_col_lbl_1 == column_lbl_1
			 and tmp_col_lbl_2 == column_lbl_2
			 and tmp_col_lbl_3 == column_lbl_3
			 and tmp_row_lbl in row_lbls):
				 cells.append(worksheet.cell(row_index, col_index).value)
		
	return cells

def generate_sketch(w, d, values=[]):
	sk = Classes.CountSketchCt(w, d, common_key)
	for v in values:
		sk.insert(v)	
	return sk

def generate_group_key(auths=[]):
	
	#get pub key from each auth
	pub_keys = []
	for auth_ip in auths:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((auth_ip, 8888))
		data = {'request':'pubkey'}
		s.send(json.dumps(data))
		result = json.loads(s.recv(1024))
		s.close()
		new_key = EcPt.from_binary(binascii.unhexlify(result['return']), G)
		print new_key
		pub_keys.append(new_key)
	
	c_pub = pub_keys[0]
	for pkey in pub_keys[1:]:
		c_pub += pkey #pub is ecpt, so we add
   
	print c_pub
	return c_pub



def load():
	
	global G
	global auths
	global common_key

	
	auths_str = sys.argv[1]
	processors_str = sys.argv[2]
	
	
	auths = auths_str.split('-')
	processors = processors_str.split('-')
	
	
	all_responsive = True
	if utilities.multiping(8888, auths):
		print "All authorities are responsive"
	else:
		all_responsive = False
		print "Not all authorities are responsive"

	if utilities.multiping(8888, processors):
		print "Processor is responsive."
	else:
		all_responsive = False
		print "Processor is not responsive."

	if all_responsive == True:
		G = EcGroup(nid=713)
		common_key = generate_group_key(auths)
		listen_on_port(8888)	




if __name__ == "__main__":
    load()
    pass
    


'''
#Test for csv parsing
common_key = y
rows = []
rows.append('E01000893')
rows.append('E01000895')
values = read_xls_cell('data/data_large.xls','iadatasheet2','Adults in Employment', 'No adults in employment in household: With dependent children','2011',rows)
cs = generate_sketch(50, 7, values)					
c, d = cs.estimate(9.0)
est = c.dec(x)
print est					
'''
					
'''
#Test from sketch creation, serialization and de-serialization
cs = Classes.CountSketchCt(50, 7, y)
cs.insert(11)
cs.insert(11)
result_str=cs.to_JSON()
obj_json = json.loads(result_str)

tmp_w = int(obj_json['vars']['w'])
tmp_d = int(obj_json['vars']['d'])

#w, d, pub
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

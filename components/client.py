import socket
import json
import sys
from petlib.ec import *
import binascii
import SocketServer
import json


from includes import utilities
from includes import Classes

G = None
auths=[]
common_key = None

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
					
					user_data = fetch_data()
					plain_sketch = generate_sketch(user_data)
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
#def parse_csv(first_row, num_of_rows, column_str): #number of rows-> how many rows counting from the first one, #column attribute of stat


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

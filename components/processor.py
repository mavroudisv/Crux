from petlib.ec import *
import binascii

import SocketServer
import json

G = None
priv = None
pub = None

def ping(ip, port):

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip, port))

	rand = random.randint(1, 99999)
	data = {'request':'ping', 'contents': {'value':rand}}
	s.send(json.dumps(data))
	result = json.loads(s.recv(1024))
	s.close()
	
	if result['return'] == rand:
		return True
	else:
		return False


def ping_all_auths(port, auths=[]):
	for a in auths:
		if not ping(a, port):
			return False
	return True
	
	
	
def listen_on_port(port, pub, priv):

	print pub
	
	server = TCPServer(('127.0.0.1', port), TCPServerHandler)
	server.serve_forever()


class TCPServer(SocketServer.ThreadingTCPServer):
	allow_reuse_address = True

class TCPServerHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		while True:
			try:
				data = json.loads(self.request.recv(1024).strip())
				print data['request'] 
				# process the data, i.e. print it:
				
				if data['request'] == 'ping':
					contents = data['contents']
					self.request.sendall(json.dumps({'return': contents['value']}))
					
				else:
					break
						
			except Exception, e:
				pass
				#print "Exception while receiving message: ", e
	
	
	
		
def load(auths=[]):
	global G
	global priv
	global pub
	G = EcGroup(nid=713)
	priv = G.order().random()
	pub = priv * G.generator()
	if ping_all_auths(auths, 8888):
		listen_on_port(8888, pub, priv)	
	else:
		print "Not all authorities are responsive"

if __name__ == "__main__":
    load()

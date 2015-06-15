import SocketServer
import socket
import random
import json

def ping(ip, port):
	
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(5.0)
		s.connect((ip, port))

		rand = random.randint(1, 99999)
		data = {'request':'ping', 'contents': {'value':rand}}
		s.send(json.dumps(data))
		result = json.loads(s.recv(1024))
		s.shutdown(socket.SHUT_RDWR)
		s.close()
	
		if result['return'] == rand:
			return True
		else:
			return False

	except Exception as e:	
		print "Exception while pinging: ", e
		return False

def multiping(port, auths=[]):
	for a in auths:
		if not ping(a, port):
			return False
	return True

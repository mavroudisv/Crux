import SocketServer
import socket
import random
import json

def ping(sock):
	
	try:
		rand = random.randint(1, 99999)
		data = {'request':'ping', 'contents': {'value':rand}}
		sock.send(json.dumps(data))
		result = json.loads(sock.recv(1024))
	
		if result['return'] == rand:
			return True
		else:
			return False

	except Exception as e:	
		print "Exception while pinging: ", e
		return False

def multiping(port, auths=[]):
	
	result = True
	for a_ip in auths:	
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#s.settimeout(120.0)
		sock.connect((a_ip, int(port)))
		if not ping(sock):
			result = False
		sock.shutdown(socket.SHUT_RDWR)
		sock.close()
	
	return result

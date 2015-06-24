import random
import json

from includes import SocketExtend as SockExt
from includes import config as conf
from includes import parser as p

def ping(sock):
	try:
		rand = random.randint(1, 99999)
		data = {'request':'ping', 'contents': {'value':rand}}
		SockExt.send_msg(sock, json.dumps(data))
		result = json.loads(SockExt.recv_msg(sock))
	
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

def alive(port, machines=[]):
	attempted = 0

	success = False
	while (attempted < conf.tries):
		try:
			if utilities.multiping(port, machines):
				success = True
				break
		except Exception as e:
			attemped += 1

	return success

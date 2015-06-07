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


def multiping(port, auths=[]):
	for a in auths:
		if not ping(a, port):
			return False
	return True

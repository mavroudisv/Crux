import socket
import json
import random



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
	


def parse_csv():
	pass
	
def generate_sketch():
	pass

def groupKey(params, pubKeys=[]):
    (G, g, h, o) = params

    pub = pubKeys[0]
    for pkey in pubKeys[1:]:
        pub += pkey
   
    return pub



def load(auths=[], processor):
	#global G
	#global priv
	#global pub
	#G = EcGroup(nid=713)
	#priv = G.order().random()
	#pub = priv * G.generator()
	if ping_all_auths(auths, 8888):
		print "All authorities are responsive"
	else:
		print "Not all authorities are responsive"

	if ping(processor, 8888):
		print "Processor is not responsive."
	else:
		print "Processor is not responsive."



if __name__ == "__main__":
    load()

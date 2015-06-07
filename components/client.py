import socket
import json
import random

from includes import utilities

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



def load():
	#global G
	#global priv
	#global pub
	#G = EcGroup(nid=713)
	#priv = G.order().random()
	#pub = priv * G.generator()
	
	auth_str = sys.argv[1]
	processors_str = sys.argv[2]
	auths = auths_str.split(' ')
	processors = processors_str.split(' ')
	
	
	if multiping(8888, auths):
		print "All authorities are responsive"
	else:
		print "Not all authorities are responsive"

	if multiping(8888, processors):
		print "Processor is not responsive."
	else:
		print "Processor is not responsive."



if __name__ == "__main__":
    load()

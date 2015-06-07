
from pprint import pprint
import time
import sys
from pprint import pprint
from fabric.api import *
from fabric.tasks import execute

import re

from automation import boto_funcs, fabric_funcs
from components import client, authority, processor



instance_ids=['i-cbb8933d']


def all_have_value(value, dictionary):
	for key in dictionary:
		tmp_value = dictionary[key]
		if value not in tmp_value:
			return False
			
	return True

def start_all(c):
	
	boto_funcs.start_instances(c, instance_ids)

	#make sure everything starts
	while True:

		states = boto_funcs.show_instances_status(c, instance_ids)
		
		if (all_have_value("running", states)):
			print "All instances STARTED."
			pprint(states)
			break
			
		time.sleep(10)
		
	return states

def stop_all(c):
	boto_funcs.stop_instances(c, instance_ids)

	#make sure everything stops
	while True:

		states = boto_funcs.show_instances_status(c, instance_ids)
		
		
		if (all_have_value("stopped", states)):
			print "All instances STOPPED."
			pprint(states)
			break
			
		time.sleep(10)

	

def main():
	
	c = boto_funcs.setup_connection()
	if len(sys.argv)> 1 and sys.argv[1] == "start":
		
		start_all(c) #fire up the instances
		
	elif len(sys.argv)> 1 and sys.argv[1] == "stop":
		stop_all(c)

	elif len(sys.argv)> 1 and sys.argv[1] == "experiment":
		
		urls = boto_funcs.get_urls_from_ids(c,instance_ids) #get their urls
		#pprint(urls)
		url_roles = boto_funcs.get_url_roles(urls)
		#pprint(url_roles)
		
		#check if we have instances of all roles
		for key in url_roles:
			if url_roles[key] == ['']:
				print "Not all instances are up!"
				sys.exit(0)
		
		env.hosts = urls.values()
		env.roledefs = url_roles
		execute(fabric_funcs.gitpull)
		execute(fabric_funcs.authority_load)
		execute(fabric_funcs.processor_load)
		execute(fabric_funcs.client_load)
		
	else:
		print "Please provide an argument."

if __name__ == "__main__":
    main()



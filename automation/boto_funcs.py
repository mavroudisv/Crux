import boto.ec2
from pprint import pprint


#Setup a connection
def setup_connection():
	conn = boto.ec2.connect_to_region("us-west-2",
	  aws_access_key_id='',
	  aws_secret_access_key='')
	return conn


#def run_instance(s):
#	conn.run_instances(
#		'<ami-image-id>',
#        key_name='myKey',
#        instance_type='c1.xlarge',
#        security_groups=['your-security-group-here'])

def start_instances(conn,instance_ids):
	instances = conn.get_all_instances(instance_ids)
	for inst in instances:
		inst.instances[0].start()

def stop_instances(conn, instance_ids):		
	conn.stop_instances(instance_ids)

def show_instances_status(conn, instance_ids):
	reservations = conn.get_all_instances(instance_ids)
	instances = [i for r in reservations for i in r.instances]
	states = {}
	for inst in instances:
		#pprint(i.__dict__)
		 states[str(inst.id)] = str(inst._state)
	return states

def get_urls_from_ids(conn, instance_ids):
	instances = conn.get_all_instances(instance_ids)
	reservations = conn.get_all_instances(instance_ids)
	instances = [i for r in reservations for i in r.instances]
	urls = {}
	for inst in instances:
		urls[str(inst.tags['Name'])]=inst.public_dns_name
		 
	return urls
	
	
def get_url_roles(urls):
	roles={}
	authority = []
	processor = []
	client = []
	for u in urls:
		if "authority" in u:
			authority.append(urls[u])
		elif "processor" in u:
			processor.append(urls[u])
		elif "client" in u:
			client.append(urls[u])
	
	roles["authority"] = authority
	roles["processor"] = processor
	roles["client"] = client
	return roles

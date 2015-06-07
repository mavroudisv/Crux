from fabric.api import *
from fabric.decorators import runs_once, roles, parallel


from base64 import b64encode, b64decode

import sys
sys.path += [ "." ]

env.user = "ubuntu"
env.key_filename = ["/home/pc/keys/ucl_tor_stats.pem"]
#env.hosts = ['ec2-52-24-151-140.us-west-2.compute.amazonaws.com', 'ec2-52-25-250-125.us-west-2.compute.amazonaws.com']
#env.roledefs={"server":["c2-52-24-151-140.us-west-2.compute.amazonaws.com"],"authority":["ec2-52-25-250-125.us-west-2.compute.amazonaws.com"]}

def prepare_machines(urls):
    names = [('ubuntu@' + u) for u in urls ]
    return names


@roles("authority")
def authority_load():
    with cd('/home/ubuntu/TorEncStats'):
		run('python test_doc.py')

@roles("processor")
def processor_load():
    with cd('/home/ubuntu/TorEncStats'):
		run('ls')

@roles("client")
def client_load():
	print "I am a client"
    #with cd('/home/ubuntu/TorEncStats'):
	#	run('ls')		
		
####GIT####
#https://github.com/mavroudisv/TorEncStats.git
#run('git clone https://github.com/mavroudisv/TorEncStats.git')

@roles("client", "processor","authority")
def gitpull():
      with cd('/home/ubuntu/TorEncStats'):
        # run('git commit -m "merge" -a')
        run('git pull')



import socket
import json
import sys
from petlib.ec import EcGroup, EcPt
from petlib.bn import Bn
import binascii
import SocketServer
import json
import csv
import time
import xlrd
from itertools import product
import datetime

from includes import config as conf
from includes import utilities
from includes import parser as p
from includes import Classes
from includes import SocketExtend as SockExt

#Globals
G = EcGroup(nid=conf.EC_GROUP)
auths=[]
common_key = None
data_dict = None
unique_id = None
num_relays = None
parsed = {}


def listen_on_port(port):
    server = TCPServer(('0.0.0.0', port), TCPServerHandler)
    server.serve_forever()


class TCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True


class TCPServerHandler(SocketServer.BaseRequestHandler):
    def handle_clean(self):
        global G
        global priv
        global pub
        global auths
        global common_key
        global parsed
        
        try:
            inp = SockExt.recv_msg(self.request).strip()                
            data = json.loads(inp)
            print "[" + str(datetime.datetime.now())[:-7] + "] Request for: " + str(data['request'])

            if data['request'] == 'stat':
                #print data['contents']
                #parameters
                contents = data['contents']
                stat_type = contents['type']
                attributes = contents['attributes']
                attr_file = attributes['file']
                attr_sheet = attributes['sheet']
                attr_column_1 = attributes['column_1']
                attr_column_2 = attributes['column_2']
                attr_column_3 = attributes['column_3']
            
                if not str(attr_column_3) in parsed:
                    rows = p.get_rows(attr_file,attr_sheet, num_relays, unique_id) #determine which rows correspond to relay
                    values = p.read_xls_cell(attr_file, attr_sheet, attr_column_1, attr_column_2, attr_column_3, rows) #load values from xls
                    parsed[str(attr_column_3)] = values
                else:
                    values = parsed[str(attr_column_3)]


                if contents['data_type'] == 'sketch':
                    sk_w = attributes['sk_w']
                    sk_d = attributes['sk_d']
                    plain_sketch = generate_sketch(int(sk_w), int(sk_d), values) #construct sketch from values
                    res = plain_sketch.to_JSON()
                    
                elif contents['data_type'] == 'values':
                    evalues = encrypt_values(values, common_key)
                    res = cts_to_json(evalues)
                
                elif contents['data_type'] == 'values_sq':
                    sq_values = square_values(values)
                    evalues = encrypt_values(sq_values, common_key)
                    res = cts_to_json(evalues)
                
                SockExt.send_msg(self.request, json.dumps({'return': res})) #return serialized sketch
                print "[" + str(datetime.datetime.now())[:-7] + "] Request served."
                
                if conf.MEASUREMENT_MODE_RELAY:
                    self.server.shutdown()
            else:
                print "Unknown request type."
                
                    
        except Exception as e:
            print "Exception on incomming connection: ", e
    
    
    def handle(self):
        if conf.MEASUREMENT_MODE_RELAY:
        
            utilities.clean_folder(conf.PROF_FOLDER)
    
            if conf.PROFILER == 'cProfiler':
                print "cProfiler active..."
                import cProfile
                import pstats
                pr = cProfile.Profile()
                pr.enable()
                self.handle_clean()
                pr.disable()
                
                #pr.dump_stats(conf.PROF_FILE_RELAY + "pickle") #pickled
                
                #readable
                sortby = 'cumulative'
                ps = pstats.Stats(pr, stream=open(conf.PROF_FILE_RELAY + "prof", 'w')).sort_stats(sortby)
                ps.print_stats()
                
                
            elif conf.PROFILER == 'LineProfiler':
                print "LineProfiler active..."
                import line_profiler
                import pstats
                import io
                pr = line_profiler.LineProfiler(self.handle_clean, get_sketches_from_relays_non_blocking
                    , Classes.CountSketchCt.aggregate, op.median_operation, op.mean_operation, op.variance_operation)
                pr.enable()
                self.handle_clean()
                pr.disable()
                
                pr.print_stats(open(conf.PROF_FILE_RELAY + "prof", 'w')) #readable
                #pr.dump_stats(conf.PROF_FILE_RELAY + "pickle") #pickled

    
            elif conf.PROFILER == "viz":
                print "Vizualization module active..."
                from pycallgraph import PyCallGraph
                from pycallgraph.output import GraphvizOutput
                from pycallgraph import Config
                
                config = Config(max_depth=conf.DEPTH)
                graphviz = GraphvizOutput()
                graphviz.output_file = conf.PROF_FILE_RELAY + 'png'
                with PyCallGraph(output=graphviz, config=config):
                    self.handle_clean()

            else:
                self.handle_clean()

        else:
            self.handle_clean()
    

def square_values(vlist):
    squared = []
    for el in vlist:
        squared.append(el*el)        
    return squared


def cts_to_json(cts):
    store_dict = {}
    i=0
    for c in cts:
        store_dict[i] = json.loads(c.to_JSON())
        i += 1
    result_dict = {'store':store_dict}
    return result_dict

    
def encrypt_values(values, key):
    enc_values = []
    for v in values:
        enc_values.append(Classes.Ct.enc(key, v))
    return enc_values
    
        
#Add values to sketch
def generate_sketch(w, d, values=[]):
    sk = Classes.CountSketchCt(w, d, common_key)
    for i,v in enumerate(values):
        sk.insert(int(v))
        #print(str(i) + "|"),
    return sk


#Compute the group public key
def generate_group_key(auths=[]):
    pub_keys = []
    for auth_ip in auths: #get pub key from each auth
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.settimeout(10.0)
        s.connect((auth_ip, conf.AUTH_PORT))
        data = {'request':'pubkey'}
        SockExt.send_msg(s, json.dumps(data))
        result = json.loads(SockExt.recv_msg(s))
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        
        new_key = EcPt.from_binary(binascii.unhexlify(result['return']), G) #De-serialize Ecpt object
        pub_keys.append(new_key)
    
    #Add keys
    c_pub = pub_keys[0]
    for pkey in pub_keys[1:]:
        c_pub += pkey #pub is ecpt, so we add
    return c_pub


def load():
    global G
    global auths
    global common_key
    global unique_id
    global num_relays
    
    auths_str = sys.argv[1]
    processors_str = sys.argv[2]
    
    unique_id = int(sys.argv[3])
    print "Relay id: " + str(unique_id)
    num_relays = int(sys.argv[4])

    try:
        skip_ping = sys.argv[5]
    except Exception as e:
        skip_ping = False
    
    auths = auths_str.split('-')
    processors = processors_str.split('-')
    
    #Make sure all components are up
    all_responsive = True
    if utilities.alive(conf.AUTH_PORT, auths) or skip_ping:
        print "All authorities are responsive"
    else:
        all_responsive = False
        print "Not all authorities are responsive"

    if utilities.alive(conf.PROCESSOR_PORT, processors) or skip_ping:
        print "Processor is responsive."
    else:
        all_responsive = False
        print "Processor is not responsive."
    
    
    if all_responsive == True: #if all components up
        common_key = generate_group_key(auths) #compute common key
        print "Common key: " + str(common_key)
        print "Listening for requests..."
        listen_on_port(conf.RELAY_PORT) #listen for requests




if __name__ == "__main__":
    load()
    


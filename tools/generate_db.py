import time
import binascii
import bsddb
from petlib.ec import *
from petlib.ec import EcGroup, EcPt
from petlib.bn import Bn


def _make_table(start=-20000, end=1000000):
    G = EcGroup(nid=713)
    g = G.generator()
    o = G.order()

    i_table = {}
    n_table = {}
    ix = start * g

    for i in range(start, end):
        i_table[str(ix)] = str(i)
        n_table[str((o + i) % o)] = str(ix)
        ix = ix + g
        #print type(ix)
        #print type(ix.export())

    return i_table, n_table
 


def generate_dbs():
    db_i_table = bsddb.btopen("i_table.db", 'c')
    db_n_table = bsddb.btopen("n_table.db", 'c')
    
    i_table, n_table = _make_table()
    
    db_i_table.update(i_table)
    db_n_table.update(n_table)
    
    db_i_table.sync()
    db_n_table.sync()
    
    db_i_table.close()
    db_n_table.close()



#G = EcGroup(nid=713)
#db_n_table = bsddb.btopen('n_table.db', 'r')
#new_d_table = {Bn.from_decimal(k):EcPt.from_binary(binascii.unhexlify(v), G) for k,v in db_n_table.items()}
#db_n_table.close()

#db_i_table = bsddb.btopen('i_table.db', 'r')
#new_i_table = {EcPt.from_binary(binascii.unhexlify(k), G):int(v) for k,v in db_i_table.items()}
#db_i_table.close()

#print new_d_table.items()
#print new_i_table.items()




#print db_n_table.keys()
#print db_n_table.items()
generate_dbs()

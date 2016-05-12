import time
import binascii
import bsddb
import os.path

from petlib.ec import *
from petlib.ec import EcGroup, EcPt
from petlib.bn import Bn

import config as conf


def _make_table(start=conf.LOWER_LIMIT, end=conf.UPPER_LIMIT):
    G = EcGroup(nid=713)
    g = G.generator()
    o = G.order()

    i_table = {}
    n_table = {}
    ix = start * g
	
    trunc_limit = conf.TRUNC_LIMIT
	
    for i in range(start, end):
        #i_table[str(ix)] = str(i) #Uncompressed
        #Compression trick
        trunc_ix = str(ix)[:trunc_limit]
        #print ix
        #print trunc_ix
        if trunc_ix in i_table:
            i_table[trunc_ix] = i_table[trunc_ix] + "," + str(i)
        else:
            i_table[trunc_ix] = str(i)
        
        
        n_table[str((o + i) % o)] = str(ix)
        ix = ix + g
        #print type(ix)
        #print type(ix.export())
        
    print "size: " + str(len(i_table))
    return i_table, n_table
 


def generate_dbs():
    cur_path = os.path.dirname(os.path.abspath(__file__)) + "/../" + conf.DB_DIR + "/"
    db_i_table = bsddb.btopen(cur_path + conf.FN_I_TABLE, 'c')
    db_n_table = bsddb.btopen(cur_path + conf.FN_N_TABLE, 'c')
    
    i_table, n_table = _make_table()
    
    db_i_table.update(i_table)
    db_n_table.update(n_table)
    
    db_i_table.sync()
    db_n_table.sync()
    
    db_i_table.close()
    db_n_table.close()



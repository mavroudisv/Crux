import sys
import time
from random import randint

from petlib.ec import *

sys.path.insert(0, '../components/includes/')
import config as conf
import Classes



def Ct_dec_unit_test(plaintext):

        G = EcGroup()
        x_1 = G.order().random()
        y_1 = x_1 * G.generator()
    
        E1 = Classes.Ct.enc(y_1, plaintext)
        E = copy(E1)

        return (E.dec(x_1) == plaintext)




for trunc in range(1,0,-1):
	Classes.reload_tables(trunc, conf.FN_I_TABLE[:-3] + "_" + str(trunc) + ".db", conf.FN_N_TABLE[:-3] + "_" + str(trunc) + ".db")     
	print "size: " + str(len(Classes._table))
	total = 0
	for i in range(100):
		print "."
		num = randint(conf.LOWER_LIMIT,conf.UPPER_LIMIT)
		tic = time.clock()
		Ct_dec_unit_test(num)
		toc = time.clock()
		total += (toc - tic)
		
		
	print str(trunc) + ": " + str(total/5)


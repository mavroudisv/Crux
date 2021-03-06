from array import array
from struct import pack
from hashlib import sha512
from copy import copy
import time
import json
import math
import binascii
import traceback
import bsddb3 as bsddb
import os.path
import sys



from petlib.ec import *
from petlib.ec import EcGroup, EcPt
from petlib.bn import Bn

import config as conf
from generate_db import *


trunc = conf.TRUNC_LIMIT #This has to match the db

# Load the precomputed decryption table
def load_table(i=conf.FN_I_TABLE, n=conf.FN_N_TABLE):	
    trunc=conf.TRUNC_LIMIT #This has to match the db
    cur_path = os.path.dirname(os.path.abspath(__file__)) + "/../" + conf.DB_DIR + "/"
    db_i_table = bsddb.btopen(cur_path + i, 'c')
    db_n_table = bsddb.btopen(cur_path + n, 'c')
    
    return db_i_table, db_n_table


def bn_sum(bn_list = []):
    bn_sum = Bn(0)
    for num in bn_list:
        bn_sum += num
    
    return bn_sum

def solve_dlp(order, base, dlp):
    
    #Bruteforce
    #for i in range(conf.LOWER_LIMIT,conf.UPPER_LIMIT):
    #    if ((i * base) == dlp): return i
    
    start_time = time.time()	
    xs = _table[str(dlp)[:trunc]].split(',')
    
    for x in xs:
        if (int(x) * base)==dlp:
            if conf.DEBUG_INFO:
                elapsed_time = time.time() - start_time
                print elapsed_time
            
            return int(x)
	
    #return int(_table[str(dlp)])


class Ct:
    @staticmethod
    def enc(pub, m):
        """ Produce a ciphertext, from a public key and message """
        if isinstance(m, int):
            m = Bn(m)
            o = pub.group.order()
            k = o.random()
            #print "k: " + str(k)
            g = pub.group.generator()
            a = k * g
            b = k * pub + EcPt.from_binary(binascii.unhexlify(_n_table[str((o + m) % o)]), G) # m * g
            return Ct(pub, a, b, k, m)
            
        else:
            """ Produce a ciphertext, from a public key and another ciphertext """
            #print "m.m: " + str(m.m)
            try:
                k = m.k
                g = pub.group.generator()
                a = k * g
                b = m.b + (k * pub)
                return Ct(pub, a, b, k, None)
            except Exception as e:
                print "Exception while encrypting ct: " + str(e)

    def dec(self, x):
        """ Decrypt a ciphertext using a secret key """
        try:
            hm = self.b - x * self.a
            o = self.pub.group.order()
            g = self.pub.group.generator()
            return solve_dlp(o, g, hm)
        except Exception as e:
            o = self.pub.group.order()
            self.self_check()
            #print("Failed to decrypt: %s" % self.m )
            raise e


    def partial_dec(self, x):
        """ Partially decrypt a ciphertext using a secret key """
        hm = self.b - x * self.a
        return hm


    def __init__(self, pub, a, b, k=None, m=None):
        """ Produce a ciphertext, from its parts """
        self.pub = pub
        self.a = a
        self.b = b
        self.k = k
        self.m = m
        
        if __debug__:
            self.self_check()

    def to_JSON(self):
        #'a': <petlib.ec.EcPt object at 0x7f3138aa03c0>,
        #'b': <petlib.ec.EcPt object at 0x7f3138aa0460>,
        #'k': 21827678495601550301649698781985954665524729557422676498904161173493,
        #'m': 2,
        #'pub': <petlib.ec.EcPt object at 0x7f3138aa0320>}

        new_k = None
        try:
             new_k = str(self.k.hex())
        except:
            pass

        new_m = None
        try:
            new_m = str(self.m.hex())
        except:
            pass
        
        #print "k: " + str(new_k)
        data = {'a':hexlify(self.a.export()), 'b':hexlify(self.b.export()), 'k':new_k, 'm':new_m, 'pub':hexlify(self.pub.export())}
        return json.dumps(data)

    def self_check(self):
        """ Runs a self check """
        if self.k is not None and self.m is not None:
            g = self.pub.group.generator()
            assert self.a == self.k * g
            assert self.b == self.k * self.pub + self.m * g



    def __add__(self, other):
        """ Add two ciphertexts, to produce a ciphertext of their sums. Also handles addition with a constant. """
        o = self.pub.group.order()
        g = self.pub.group.generator()

        if isinstance(other, int):
            # Case for int other
            new_b = self.b + EcPt.from_binary(binascii.unhexlify(_n_table[str((o + other) % o)]), G) # other * g
            new_k, new_m = None, None
            if self.k is not None:
                new_m = self.m + other # self.m.mod_add( other, o)
            return Ct(self.pub, self.a, new_b, self.k, new_m)
        else:
            # Case for ciphertext other
            if __debug__:
                assert self.pub == other.pub
            new_a = self.a + other.a
            new_b = self.b + other.b
            new_k, new_m = None, None
            if self.k is not None and other.k is not None:
                new_k = self.k.mod_add( other.k, o)
                new_m = self.m + other.m # self.m.mod_add(other.m, o)
            return Ct(self.pub, new_a, new_b, new_k, new_m)



    @staticmethod
    def sum(elist):
        """ Sums a number of Cts """
        pub = elist[0].pub
        G = pub.group
        # w = [Bn(1) for _ in range(len(elist))]
        as_l = [e.a for e in elist]
        bs_l = [e.b for e in elist]
        ks_l = [e.k for e in elist]
        ms_l = [e.m for e in elist]
        
        #from pprint import pprint
        #pprint(ks_l)
        
        new_a = G.sum(as_l)
        new_b = G.sum(bs_l)
        try:
            new_k = bn_sum(ks_l)
        except Exception as e:
            print "Exception in sum of Cts: " + str(e)        
            
        new_m = bn_sum(ms_l)

        return Ct(pub, new_a, new_b, new_k, new_m)

    def __rmul__(self, other):
        if isinstance(other, int):
            """ Multiples an integer with a Ciphertext """
            o = self.pub.group.order()
            new_a = other * self.a 
            new_b = other * self.b
            new_k, new_m = None, None
            if self.k is not None:
                new_k = self.k.mod_mul( other, o)
                new_m = self.m.mod_mul( other, o) 
            return Ct(self.pub, new_a, new_b, new_k, new_m)
            
                        
            

    def __neg__(self):
        """ Multiply the value by -1 """
        o = self.pub.group.order()
        new_a = -self.a 
        new_b = -self.b
        if self.k is not None and self.m is not None:
            new_k = (o - self.k) % o
            new_m = - self.m
        else:
            new_k = None
            new_m = None

        return Ct(self.pub, new_a, new_b, new_k, new_m)

    def rnd(self):
        """ Re-randomize a ciphertext """
        E0 = Ct.enc(self.pub, 0)
        return self + E0


def hashes(item, d, packed):
    """ Returns d hashes / positions for the item """
    codes = []
    
    encoded = item.encode("utf8")
    i = 0
    while len(codes) < d:
        codes += list(array('I', sha512(packed[i] + encoded).digest()))
        i += 1
    return codes[:d]


class CountSketchCt(object):
    """ A Count Sketch of Encrypted values """


    
    @staticmethod
    def epsilondelta(epsilon, delta, pub):
        w = int(math.ceil(math.e / epsilon))
        d = int(math.ceil(math.log(1.0 / delta)))
        return CountSketchCt(w, d, pub, epsilon, delta)

    def __init__(self, w, d, pub, eps=0, dlt=0):
        """ Initialize a w * d Count Sketch under a public key """

        if __debug__:
            assert isinstance(w, int) and w > 0
            assert isinstance(d, int) and d > 0

        self.pub = pub
        self.d, self.w = d, w
        self.epsilon = eps
        self.delta = dlt
        
        self.packed = []
        for i in range(d):
            self.packed.append(pack("I", i))
        
        #No dont do this...
        #self.store = [ [Ct.enc(pub, 0)] * w for _ in range(d) ]

        #Do this instead...
        self.store = [ [Ct.enc(pub, 0) for i in range(w)] for j in range(d) ]

    def to_JSON(self):
        #'d': 7,
        #'pub': <petlib.ec.EcPt object at 0x7f4b692c5050>,
        #'store': [[<includes.Classes.Ct instance at 0x7f4b692c3b48>,
        #'w': 50}

        variables_dict = {'pub':hexlify(self.pub.export()), 'd':str(self.d), 'w':str(self.w)}     
        
        store_dict = {}
        i=0
        for row in self.store:
            row_str = ''
            for cell in row:
                store_dict[i] = json.loads(cell.to_JSON())
                i += 1
                
            
        result_dict = {'vars':variables_dict, 'store':store_dict}
        
        return json.dumps(result_dict)

    def load_store_list(self, w, d, store_dict):
        counter = 0        
        for i in range(d):
            for j in range(w):                
                contents = store_dict[str(counter)]
    
                try:                    
                    self.store[i][j] = Ct(EcPt.from_binary(binascii.unhexlify(contents['pub']),G), EcPt.from_binary(binascii.unhexlify(contents['a']),G), EcPt.from_binary(binascii.unhexlify(contents['b']),G), Bn.from_hex(contents['k']), Bn.from_hex(contents['m']))
                    counter += 1
                except Exception as e:
                    print "Exception while loading sketch store matrix: " + str(e)
                    traceback.print_exc()
                 
                
    
    def print_details(self):
         for i in range(self.d):
             for j in range(self.w):
                 print self.store[i][j].a           
             print "---------"

    def dump(self):
        from cStringIO import StringIO
        from struct import pack

        dst = StringIO()
        dst.write(pack("II", self.d, self.w))

        for di in range(self.d):
            for wi in range(self.w):
                ba = self.store[di][wi].a.export()
                dst.write(pack("I", len(ba)))
                dst.write(ba)
                
                bb = self.store[di][wi].b.export()
                dst.write(pack("I", len(bb)))
                dst.write(bb)

        return dst.getvalue()
                


    def insert(self, item):
        """ Insert an element into the encrypted count sketch """
        try:
            item = str(item)
            h = hashes(item, self.d, self.packed)
            for di in range(self.d):
                self.store[di][h[di] % self.w] += 1 
 
            self.store[di][h[di] % self.w].self_check()
        except Exception as e:
           print "Exception on insert: ", e
            
            
    def estimate(self, item):
        """ Estimate the frequency of one value """

        item = str(item)
        h = hashes(item, self.d, self.packed)
        h2 = []
        for hi in h:
            v = hi - 1 if hi % 2 == 0 else hi + 1
            h2 += [v]

        g = self.pub.group.generator()
        o = self.pub.group.order()

        elist = []
        for i, [hi, hpi] in enumerate(zip(h, h2)):
            v1 = self.store[i][hi % self.w] 
            v2 = self.store[i][hpi % self.w]
            elist += [v1, -v2]
        
        estimates = Ct.sum(elist)
        
        return estimates, self.d

    @staticmethod
    def aggregate(others):
        o0 = others[0]
        pub, w, d, epsilon, delta = o0.pub, o0.w, o0.d, o0.epsilon, o0.delta

        if __debug__:
            for o in others:
                assert pub == o.pub
                assert w == o.w and d == o.d
        
        cs = CountSketchCt(w, d, pub, epsilon, delta)

        for di in range(d):
            for wi in range(w):
                elist = []
                for o in others:
                    elist += [o.store[di][wi]]
                cs.store[di][wi] = Ct.sum(elist)


        return cs



def get_median(cs, min_b = 0, max_b = 1000, steps = 20):
    L, R = 0, 0
    bounds = [min_b, max_b]
    total = None

    for _ in range(steps):
        old_bounds = copy(bounds)
        # print(bounds)

        cand_median = int((bounds[1] + bounds[0]) / 2)

        if bounds[0] == cand_median:
            yield cand_median
            return

        EL = Ct.sum([ cs.estimate(i)[0] for i in range(bounds[0], cand_median) ])
        newl = yield EL # EL.dec(sec)
        
        if total is None:
            ER = Ct.sum([ cs.estimate(i)[0] for i in range(cand_median, bounds[1]) ])        
            newr = yield ER # ER.dec(sec)

            total = newl + newr
            # print("total: %s" % total)

        else:
            newr = total - newl
            if __debug__:
                ER = Ct.sum( [ cs.estimate(i)[0] for i in range(cand_median, bounds[1]) ])        
                newrx = yield ER # ER.dec(sec)
                # assert newrx == newr

        if newl + L > newr + R:
            R = R + newr
            bounds[1] = cand_median
            total = newl
        else:
            L = L + newl
            bounds[0] = cand_median
            total = newr

        if bounds == old_bounds:
            yield cand_median
            return 


def reload_tables(trunc_new, i=conf.FN_I_TABLE, n=conf.FN_N_TABLE):
    #print "Warning: Remember to set the trunc limit yourself!"
    global trunc
    global _table
    global _n_table
    
    #del _table
    #del _n_table
    trunc=trunc_new
    _table, _n_table = load_table(i, n)



########Tests#########
def unit_tests():
    return CountSketchCt_unit_test() and Ct_dec_unit_test()

def CountSketchCt_unit_test():

        G = EcGroup()
        x = G.order().random()
        y = x * G.generator()
        cs = CountSketchCt(50, 7, y)
        cs.insert(11)
        c, d = cs.estimate(11)
        
        est = c.dec(x)
        #assert est == d
        return est == d

        
def Ct_dec_unit_test():
    try:    
        G = EcGroup()
        x_1 = G.order().random()
        y_1 = x_1 * G.generator()
    
        x_2 = G.order().random()
        y_2 = x_2 * G.generator()

        x_3 = G.order().random()
        y_3 = x_3 * G.generator()
    
        #
        E1 = Ct.enc(y_1+y_2, 2)
        E = copy(E1)
        E.b = E1.partial_dec(x_1)
        
        
        #
        E3 = Ct.enc(y_1, 22)
        E4 = Ct.enc(y_2+y_3, E3)
        E5 = copy(E4)
        E5.b = E4.partial_dec(x_1)
        
        return ((E.dec(x_2) == 2) and (E1.dec(x_1+x_2) == 2) and (E5.dec(x_2+x_3)==22))
        
    except Exception:
        return False




        
G = EcGroup(nid=conf.EC_GROUP)
cur_path = os.path.dirname(os.path.abspath(__file__)) + "/../" + conf.DB_DIR + "/"
if (not os.path.isfile(cur_path + conf.FN_I_TABLE)) or (not os.path.isfile(cur_path + conf.FN_N_TABLE)):
    print "Precomputation tables not found. Generating...",
    sys.stdout.flush()
    generate_dbs()
    print "Done"

print "Loading precomputation tables...",
_table, _n_table = load_table()
print "Done"

#Port Settings
AUTH_PORT = 6666
CLIENT_PORT= 7777
PROCESSOR_PORT=8888

#Crypto settings
EC_GROUP = 713

#Sketch settings
EPSILON = 0.05
DELTA = 0.0005


#Ping settings
TRIES = 1

#Files
FN_I_TABLE = 'data/i_table.db'
FN_N_TABLE = 'data/n_table.db'


#Optimizations
COMPRESS = False


FAST_PARSING = False

#Measurements
MEASUREMENT_MODE_AUTHORITY = False
MEASUREMENT_MODE_PROCESSOR = True
MEASUREMENT_MODE_CLIENT = False
MEASUREMENT_MODE_USER = False
PROFILER = "cProfiler"

PROF_FILE_PROCESSOR = "prof_proc."
PROF_FILE_CLIENT = "prof_client."
PROF_FILE_AUTHORITY = "prof_auth."
PROF_FILE_USER = "prof_user."


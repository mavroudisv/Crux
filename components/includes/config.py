#Port Settings
AUTH_PORT = 6666
CLIENT_PORT= 7777
PROCESSOR_PORT=8888

#Crypto settings
EC_GROUP = 713
DP = True

#Sketch settings
EPSILON = 0.05
DELTA = 0.0005


#Ping settings
TRIES = 5

#Files
FN_I_TABLE = 'data/i_table.db'
FN_N_TABLE = 'data/n_table.db'

#Debug
SHOW_LEN = False

#Optimizations
COMPRESS = False

#Measurements
MEASUREMENT_MODE_AUTHORITY = False
MEASUREMENT_MODE_PROCESSOR = False
MEASUREMENT_MODE_CLIENT = False
MEASUREMENT_MODE_USER = False
DEPTH = 1
PROFILER = "viz"

PROF_FOLDER = "../profiling_results"
PROF_FILE_PROCESSOR = "../profiling_results/prof_proc."
PROF_FILE_CLIENT = "../profiling_results/prof_client."
PROF_FILE_AUTHORITY = "../profiling_results/prof_auth."
PROF_FILE_USER = "../profiling_results/prof_user."


#Encrypted Statistics for Tor


TES is a complete system enabling end-users to submit queries for statistics on private data 

##Overview

The system currently supports:
* Median
* Mean
* Variance

it can be further extended for the computation of other statistics.


##Components


### Query processor

### Clients

### Encryption Authorities

### End-User Interface


## Usage

To start the authorities, the clients, and the query processor:

`python main.py start`

when all instances are loaded:

`python main.py experiment`

Then request a specific statistic:

`python user.py -s "processor_ip" -p "processor_port" --stat "stat_type" "strings" "which specify" "the column in the xls"`

an example would be:

`python user.py -s 52.26.142.27 -p 8888 --stat variance "Lone Parents" "Lone parents not in employment" 2011`


##Requirements

* Fabric
* Boto
* petlib
* 

##Future Improvements

* Support adding new authorities on the fly
* Django user interface

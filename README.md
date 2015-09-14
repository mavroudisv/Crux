#Crux: Privacy-preserving Statistics for Tor


Crux is a complete system enabling end-users to submit queries for statistics on private data, collected as a stream from the TOR network.

##Overview

The system currently supports:
* Median
* Mean
* Variance

it can be further extended for the computation of other statistics.



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
The project was developed and tested in python 2.7. Please let me know if it works/or not on a different version.

The following packages are also needed and you should install them if they are not already installed on your system:

* Fabric
* Boto
* petlib
* socketServer
* xlrd
* binascii

Most of them can be installed using `pip`, but look on their project websites for detailed instructions.

##Future Improvements

* Support other statistics
* Support adding new authorities on the fly
* Django user interface
* Ephimeral Keys

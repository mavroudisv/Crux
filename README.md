#Crux: Privacy-preserving Statistics for Tor


Crux is a complete system enabling end-users to submit queries for statistics on private data, collected as a stream from the TOR network.

The system currently supports:
* Median
* Mean
* Variance

it can be further extended for the computation of other statistics.



## Usage

For a testing setup we need:



1. An Authority

	To start the relay we use a terminal command in the form:

	`python authority.py`


1. A query processor


	To start the relay we use a terminal command in the form:

	python processor.py AUTH_IP_1-AUTH_IP_2 RELAY_IP_1-RELAY_IP_2


	An example would be:

	`python processor.py 127.0.0.1 127.0.0.1`


1. A relay

	To start the relay we use a terminal command in the form:

	python relay.py AUTH_IP_1-AUTH_IP_2 RELAY_IP_1-RELAY_IP_2 RELAY_ID NUM_OF_RELAYS




An example would be:

`python relay.py 127.0.0.1 127.0.0.1 0 1`


When all the above components are loaded, the user script can then be used to submit requests in the form:

`python user.py -s "processor_ip" -p "processor_port" --stat "stat_type" "strings" "which specify" "the column in the xls"`

an example would be:

`python user.py -s 52.26.142.27 -p 8888 --stat variance "Lone Parents" "Lone parents not in employment" 2011`


However, keep in mind that in an actual setup at least 2 (non-actively malicious) relays should be used.


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

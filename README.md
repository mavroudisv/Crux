## Crux in a nutshell


Crux is a privacy-preserving system, aiming to provide aggregated statistics for distributed deployments.

More specifically, it is often the case that the statistics collected by the individual nodes of a distributed system contain sensitive information which should not be publicaly released.
On the other hand, aggregated statistics over the entire network are very useful for administrators, developers, users etc. Crux uses privacy enhancing technologies to compute statistics
for the whole deployment, while it preserves the confidentiality of the individual measurements reported by the nodes.

The novelty of Crux, is that it is not project specific and hence it is an ideal platform for the development of a general purpose privacy-preserving analytics service.


The system currently supports:
* Sum
* Median
* Mean
* Variance

we are also working on adding other statistics (requests welcome!).


## Usage

For a testing setup we need:



1. An Authority


	To start the authority the terminal command is in the form:

	`python authority.py`




2. A query processor

	To start the query processor the terminal command is in the form:

	`python processor.py AUTH_IP_1-AUTH_IP_2 RELAY_IP_1-RELAY_IP_2`


	An example would be:

	`python processor.py 127.0.0.1 127.0.0.1`


3. A relay

	To start the relay the terminal command is in the form:

	`python relay.py AUTH_IP_1-AUTH_IP_2 PROCESSOR_IP RELAY_ID NUM_OF_RELAYS`




	An example using a dummy dataset would be:

	`python relay.py 127.0.0.1 127.0.0.1 0 1`


	It should be noted that in its current form the relay component is only able to parse data only from xls files.



4. When all the above components are loaded, the user script can then be used to submit requests in the form:

	`python user.py -s "processor_ip" -p "processor_port" --stat "stat_type" "strings" "which specify" "the column in the xls"`

	an example would be:

	`python user.py -s 127.0.0.1 -p 8888 --stat median "Lone Parents" "Lone parents not in employment" 2011`


	The parameters of the statistic (e.g. "Lone Parents" "Lone parents not in employment" 2011) depend on the specific application/data. The details seen here correspond to our testing dataset.

	However, keep in mind that in an actual setup at least 2 (non-actively malicious) relays should be used.


## Requirements
The project was developed and tested in python 2.7. Please let me know if it works/or not on a different version.

The following packages are also needed and you should install them if they are not already installed on your system:

* Fabric
* Boto
* petlib
* socketServer
* xlrd
* binascii
* bsddb3

Most of them can be installed using `pip`, but look on their project websites for detailed instructions.


## Notes

When running the authority for first time the tables of precomputed values will be generated need to be generated. Depending on your hardware specifications this will normally take few minutes. With the default settings, the total size of the database files will be ~300MB, however we are working to reduce this.


## Future Improvements

* Support other statistics
* Support adding new authorities on the fly
* Django user interface
~~* Ephimeral Keys~~

Scrap the hospital data and display it on google map
====================================================
 It's simple scraping application for scrap the data from website , and store it to mysql db than display it on maps based on address 

Installation
============
Cloning this repository to your machine, create a virtual environment and install the requirements.

[----- For Linux and Mac users ----]

	$ virtualenv venv
    $ source venv/bin/activate
    (venv) $ pip install -r requirements.txt

Running
=======
To run this application by using following command:

	1) Create db in mysql and import the db.sql
		
		a) mysql -u root -p

		b) create database hospital

		c) exit

		d) mysql -u root -p hospital < db.sql

	2) scrap the top four hospital data custom site
		
		(venv) $ python scrap_hospitals.py 

	3) find geolocation and make json file(hospital_location.json) for hospitals
		
		venv) $ python make_json_file.py

Output
======
	To view hospital_location.html on browser


Note : Please change the file name, url, database settings in config.cnf

    

import ConfigParser
import pymysql.cursors
import urllib, urllib2, json
from pygeocoder import Geocoder

config = ConfigParser.ConfigParser()
config.read("config.cnf")

hospital_data = []

class Tojson(object):
	def __init__(self):
		global connection
		connection = pymysql.connect(host=config.get('mysql','host'),
                                     user=config.get('mysql','user'),
                                     password=config.get('mysql','password'),
                                     db=config.get('mysql','db'),
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

	def get_address_as_json(self):
		global connection
		try:
			with connection.cursor() as cursor:
				cursor.execute ("select hospital_address,hospital_name from  "+ config.get("mysql","table"))
				data = cursor.fetchall()
				for row in data:
					self.get_lat_long(row['hospital_address'],row['hospital_name'])
			
			with open(config.get('outputfile','hospital_address'), "w") as myfile:
				myfile.write("hospitals = '"+json.dumps(hospital_data)+"'")  
		
		except Exception as e:
			print(e)

	def get_lat_long(self, address, hospital_name):
		try:
			if(Geocoder.geocode(address).valid_address == True):
				results = Geocoder.geocode(address)
				temp = {}
				temp['hospital_name'] = hospital_name.replace("'", "")
				temp['lat'] = results.latitude
				temp['lon'] = results.longitude
				hospital_data.append(temp)
		except Exception as e:
			pass

Tojson().get_address_as_json()



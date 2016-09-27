import sys
import os
import ConfigParser
import logging
import json
import urlparse
import re
import pymysql.cursors

#Web scraping
from bs4 import BeautifulSoup
import requests

config = ConfigParser.ConfigParser()
config.read("config.cnf")

#Logging
log_path = config.get('logging', 'log_path')
log = None

main_url = config.get('url','main_url')


page_links = []
hospital_information = []



class Scrap(object):

    def __init__(self):
        global connection
        print "Initiating.."
        # Connect to the database
        connection = pymysql.connect(host=config.get('mysql','host'),
                                     user=config.get('mysql','user'),
                                     password=config.get('mysql','password'),
                                     db=config.get('mysql','db'),
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)

    # Main function to initiate the process
    # i/p - main_url
    # o/p - insert data to db
    def main(self, url):
        try:
            if(url):
                page_links.append(url)
                page_content = self.parse_url(url)
                if(page_content):
                    self.get_pages(page_content)
                    if(page_links):
                        self.get_hospital()
                        if(hospital_information):
                            self.insert_db(hospital_information)
        except Exception as e:
            print(e)
            return 0
    
    #Parse the page
    #i/p - url
    #o/p - page_content         
    def parse_url(self,url):
        try:        
            if(url):
                page_content = ""
                print("Parse the page - "+str(url))
                response = requests.get(url)
                if(response.status_code == 200):
                    print("Response received")
                    page_content = response.text
                    return page_content
                else:
                    print("Data retrieval failed. Received responsed from the web page: " + str(response.status_code))
                    return 0
            else:
                print "url is empty"
                return 0
        except Exception as e:
            print(e)
            return 0

    #Get all page links from pagination
    #i/p - main page_content
    #o/p - page links
    def get_pages(self, page_content):
        try:
            if(page_content):
                soup = BeautifulSoup(page_content, "html5lib")
                page_numbers = soup.find("div", {"id": "CPH_TP_PageNumbers"})                
                if page_numbers is not None:
                    page_number = page_numbers.findAll("a")    
                    for page in page_number:
                        if page.get('href') != '' and  page.get('href') != 'javascript:void(0)':
                            page_links.append(str(main_url) + str(page.get('href')))
            else:
                print "No Pages Found" 
                return 0
        except Exception as e:
            print(e)
            return 0

    #Get the top 4 hospitals data from each page 
    #o/p - hospital information
    def get_hospital(self):
        try:
            if(page_links):                
                for link in page_links:           
                    page_content = self.parse_url(link.strip())
                    if(page_content):
                        soup = BeautifulSoup(page_content, "html5lib")

                        
                        hospital_data = soup.findAll('div',{'class','LIT'})
                        if(hospital_data):
                            count = 0
                            for data in hospital_data:
                                if data.find('h2') is not None:
                                    count += 1 
                                    temp_data = {}
                                    temp_data['hospital_name'] = data.find('h2').text

                                    keys =  re.findall('<b>(.*?)</b>', str(data), re.DOTALL)
                                    values = re.findall('</b>(.*?)<br/>', str(data), re.DOTALL)

                                    for index, key in enumerate(keys):
                                        key = key.strip().replace(':','').replace(' ','').lower()                                        
                                        if("category" in key):
                                            temp_data['category'] = values[index]
                                        if("hospitaladdress" in key):
                                            temp_data['hospital_address'] = values[index]
                                        if("pincode" in key):
                                            temp_data['pin_code'] = values[index]
                                        if("phonenumber" in key):
                                            temp_data['phone'] = re.sub(r'[-|(|)]',r'',values[index]).split("/")[0].replace(" ", "")[0:11]
                                    hospital_information.append(temp_data)
                                    if count == 4:
                                        count = 0
                                        break
                        else:
                            print "Content is empty"                             
               
        except Exception as e:
            print(e)
            return 0
    
    #Insert the data to mysql db
    #i/p - hospital information
    def insert_db(self, hospital_information):
        global connection
        try:
            with connection.cursor() as cursor:
                for data in hospital_information:
                    sql = "INSERT INTO " + config.get('mysql','table') +  " (`hospital_name`, `category`, `hospital_address`, `pin_code`, `phone`) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (data['hospital_name'], data['category'], data['hospital_address'], int(data['pin_code']), int(data['phone'])))
                    print "Insert Success"
                    connection.commit()
        except Exception as e:
            print(e)
            return 
        finally:
            cursor.close()
            connection.close()

Scrap().main(sys.argv[1])
#Scrap().get_hospital()

from bs4 import BeautifulSoup
import requests
import string
import logging

class ScraperMedline:

	def __init__(self):

		self.base_url = "https://medlineplus.gov/druginfo/"
		

	def getCategories(self):

		letters = string.ascii_uppercase
		result = list(map(lambda letter: self.base_url+"drug_{}a.html".format(letter),letters))
								#"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		result.append(self.base_url + "drug_00.html")

		return result
	

	def getSource(self,url):

		r = requests.get(url)

		if r.ok == True: 
			if r.status_code == 200:
				try:
					return BeautifulSoup(r.content,"lxml")
				except:
					logging.info("!pip3 install lxml")	
			else:
				logging.error("Your status code == {}".format(status_code))
		else:
			logging.warning("Check the problem and try again.")


	def getAllDrugsLinks(self,source):
		""" html#drug-index.us > body > div#mplus-wrap > div#mplus-content > article > ul#index """
		

		#return list(map(
		#	lambda drug: self.base_url+drug.find("a").get("href").replace(".","",1),
		#	set(
		#		source.find("ul", attrs={"id":"index"}).find_all("li"))
		#	))

		""" ./meds/a601050.html --> base_url+ /meds/a601050.html """
		
		drug_elements = source.find("ul", attrs={"id":"index"}).find_all("li")
		drug_links = list(map(lambda drug: self.base_url + drug.find("a").get("href").replace(".","",1),drug_elements))
		return set(drug_links)



		
		
		

if __name__ == '__main__':
	scraper = ScraperMedline()
	source = scraper.getSource("https://medlineplus.gov/druginfo/drug_Aa.html")
	drugs = scraper.getAllDrugsLinks(source)
	print(len(drugs))
	print(drugs)
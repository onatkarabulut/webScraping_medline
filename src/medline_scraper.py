from bs4 import BeautifulSoup
import requests
import string
import logging
from tqdm import tqdm


class ScraperMedline:

    def __init__(self):
        self.base_url = "https://medlineplus.gov/druginfo/"
        self.drug_links = set() 

    def getCategories(self):
        letters = string.ascii_uppercase
        result = list(map(lambda letter: self.base_url+"drug_{}a.html".format(letter),letters))
                                #"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result.append(self.base_url + "drug_00.html")
        return result
    

    def getSource(self,url):
        try:
            r = requests.get(url)			
            if r.status_code == 200:
                try:
                    return BeautifulSoup(r.content,"lxml")
                except ModuleNotFoundError:
                    logging.error("""::MODULE NOT FOUND::""")	
            else:
                logging.error("Your status code == {}".format(r.status_code))
            
        except requests.exceptions.HTTPError as e:
            return "Error" + str(e)

    def getAllDrugsLinks(self,source):
        """ html#drug-index.us > body > div#mplus-wrap > div#mplus-content > article > ul#index """
        
        try:
            #drug_elements = source.find("ul",attrs={"id":"index"}).find_all("li")
            drug_links = list(map(lambda drug: self.base_url + drug.find("a")
                .get("href")
                .replace(".","",1),
                #drug_elements
                source
                .find("ul",attrs={"id":"index"})
                .find_all("li")
                ))
            return set(drug_links) 
            """ ./meds/a601050.html --> base_url+ /meds/a601050.html """
        except Exception as e:
            raise e


    def findAllDrugLinks(self):
        categories = self.getCategories()
        try:
            bar = tqdm(categories,unit=" category link")
            for categories_link in bar:
                bar.set_description(categories_link)
                categories_source = self.getSource(categories_link)
                result = self.getAllDrugsLinks(categories_source)
                self.drug_links = self.drug_links.union(result)
        except ModuleNotFoundError:
            logging.error("""::MODULE NOT FOUND::""")
        return self.drug_links
    
        


    def getName(self,source):
        try:
            return source.find("h1", attrs={"class":"with-also"})
        except Exception:
            return False
        

    def scrapeDrugs(self):
        result = list()
        links = self.findAllDrugLinks()
        for link in links:
            drug_source = self.getSource(link)
            name = self.getName(drug_source)
            result.append(dict(
                 name=name,
                 url= link
                 ))
        return result
   
   
if __name__ == '__main__':
    scraper = ScraperMedline()
    data = scraper.scrapeDrugs()
    print(data)
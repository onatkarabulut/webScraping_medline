import string
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import logging
import click

class MedlineScraperProject:
    def __init__(self):
        self.base_url = "https://medlineplus.gov/druginfo"
        self.drug_links = set()

    def getCategories(self):
        letters = string.ascii_uppercase
        result = list(map(lambda letter: self.base_url + "/drug_{}a.html".format(letter),letters))
                                        #"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result.append("https://medlineplus.gov/druginfo/drug_00.html")
        return result

    def getSource(self, url):
        r = requests.get(url)
        if r.status_code == 200: return BeautifulSoup(r.content,"lxml") #!pip install lxml
        return logging.error("Your status code == {}".format(r.status_code))
            
    def getAllDrugsLinks(self,source):
        """ html#drug-index.us > body > div#mplus-wrap > div#mplus-content > article > ul#index """
        drug_elements = source.find("ul", attrs={"id":"index"}).find_all("li")
        drug_links = list( map(
                lambda drug: self.base_url + drug.find("a").get("href").replace(".","",1), drug_elements
                ))
        return set(drug_links)
        """ ./meds/a601050.html --> base_url+ /meds/a601050.html """


    def findAllDrugLinks(self):
        categories = self.getCategories()
        bar = tqdm(categories,
                   unit=" category link")
        for category_link in bar:
            bar.set_description(category_link)
            category_source = self.getSource(category_link)
            result = self.getAllDrugsLinks(category_source)
            self.drug_links = self.drug_links.union(result)
        return self.drug_links

    def getName(self,source):
        try:
            return source.find("h1", attrs={"class":"with-also"}).text
        except Exception:
            return None

    def getSectionInfo(self, source, id_element):
        try:
            title = source.find("div", 
                                attrs={"id":id_element}).find("h2"
                                    ).text
            
            content = source.find("div", 
                                  attrs={"id":id_element}).find("div",
                                                                attrs={"class": "section-body"
                                                                       }).text
            return dict(
                title=title,
                content=content
            )
        except Exception:
            return None


    def scrapeDrugs(self, start, end):
        if start is None:
            start = 0

        result = list()
        links = list(self.findAllDrugLinks())
        if end is None:
            end = len(links)

        bar = tqdm(links[start:end],
                   unit=" drug link")
        
        for link in bar:
            sections = list()
            bar.set_description(link)
            drug_source = self.getSource(link)
            name = self.getName(drug_source)
            why = self.getSectionInfo(drug_source, "why")
            how = self.getSectionInfo(drug_source, "how")
            other_uses = self.getSectionInfo(drug_source, "other-uses")
            precautions = self.getSectionInfo(drug_source,"precautions")
            special_dietary = self.getSectionInfo(drug_source,"special-dietary")
            side_effects = self.getSectionInfo(drug_source,"side-effects")
            overdose = self.getSectionInfo(drug_source,"overdose")
            other_information = self.getSectionInfo(drug_source,"other-information")
            brand_name_1 = self.getSectionInfo(drug_source,"brand-name-1")
            sections.append(why)
            sections.append(how)
            sections.append(other_uses)
            sections.append(precautions)
            sections.append(special_dietary)
            sections.append(side_effects)
            sections.append(overdose)
            sections.append(other_information)
            sections.append(brand_name_1)            
            
            # self.sectionInfoRt("why",link)
            
            
            result.append(dict(name=name,url=link,sections=sections))
        return result
    
    # def sectionInfoRt(self,name,link):
    #     name = self.getSectionInfo(link,self.replaceUnderline(link))
        
    #     pass

    # def replaceUnderline(self,title_text):
    #     pass
    
    def jsonWriter(self,data,filename="result.json"):
        with open(filename, "w", encoding="utf-8") as file:
            file.write(json.dumps(data,indent=2))
            
            
if __name__ == '__main__':

    @click.command()
    @click.option("--start",
                  type=int,
                  help = "[EN] Where does it start?\nExample: --start 0 or --start 100\nIf you do not enter a value, it will start from 0.\n[TR] Nereden başlasın?\nÖrnek: --start 0 veya --start 100\nEğer bir değer girmezseniz 0'dan başlayacaktır.",
                  default = 0)
    @click.option("--end",
                  type=int,
                  help="[EN] Where does it end?\nExample: --end 25 or --end 1000\nIf you do not enter a value, it will stop at 50.\n[TR] Nerede dursun?\nÖrnek: --end 25 veya --end 100\nEğer bir değer girmezseniz 20'de duracaktır.",
                  #default = 10
                  )
    @click.option("--filename",
                  help = "[EN] Enter a filename.\nExample: --filename medline_scraper.json\nIf you don't enter a name, it will save as default.\n[TR] Dosya adı giriniz.\nÖrnek: --filename medline_kazıma.json\nEğer bir isim girmezseniz varsayılan değer olarak kaydedilir.",
                  default = "data.json",
                  type=str)
    def run(start,end, filename):
        scraper = MedlineScraperProject()
        data = scraper.scrapeDrugs(start, end)
        scraper.jsonWriter(data, filename)
    run()
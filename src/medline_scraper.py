import string

class ScraperMedline:

	def __init__(self):
		self.base_url = "https://medlineplus.gov/druginfo/"
		
	def getCategories(self):
		letters = string.ascii_uppercase
		result = list(map(lambda letter: self.base_url+"drug_{}a.html".format(letter),letters))#"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		result.append(self.base_url + "drug_00.html")
		return result

if __name__ == '__main__':
	scraper = ScraperMedline()
	print(*scraper.getCategories(),sep="\n")
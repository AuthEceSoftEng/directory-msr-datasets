import os
import json
import time
import requests
from bs4 import BeautifulSoup

# Note that you already have to have access to the papers (e.g. using your university computer).
# This script does not give you access to any papers not already supported by your access rights.
# Papers are licensed in their corresponding publishers, so they are not included in this repository.

def getACMPDF(doi):
	# Get pdf
	r = requests.get("https://dl.acm.org/doi/pdf/" + doi, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'})
	time.sleep(20)

	# Return paper pdf
	return r.content

def getIEEEPDF(doi):
	# Get ieee number
	r = requests.get("https://doi.org/" + doi, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'})
	time.sleep(10)

	# Get pdf link
	pdflink = "http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&isnumber=&arnumber=" + r.url.split("/")[-2]
	r = requests.get(pdflink, headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'})
	time.sleep(10)

	# Return paper pdf
	return r.content

def getPDF(doi, year):
	if int(year) in [2014, 2016, 2018, 2020, 2022, 2024]:
		return getACMPDF(doi)
	elif int(year) in [2013, 2015, 2017, 2019, 2021, 2023]:
		return getIEEEPDF(doi)

if not os.path.exists("../_data/paperdocuments"):
	os.makedirs("../_data/paperdocuments")

datapapers = []
with open("../_data/msrdatapapersperyear.json") as infile:
	datapapers = json.load(infile)

for year in datapapers:
	if int(year) == 2022 or int(year) == 2024:
		for paperdoi in datapapers[year]:
			paperid = "MSR" + year + "_" + "_".join(paperdoi.split("/"))
			if not os.path.exists("../_data/paperdocuments/" + paperid + ".pdf"): # paper document not already retrieved
				print("Retrieving document for paper " + paperid)
				paperdocument = getPDF(paperdoi, year)
				if paperdocument is not None:
					with open("../_data/paperdocuments/" + paperid + ".pdf", 'wb') as outfile:
						outfile.write(paperdocument)
				print("Document retrieved")

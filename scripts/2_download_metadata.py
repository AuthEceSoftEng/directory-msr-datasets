import os
import json
import time
import requests

def request_for_metadata(doi):
	r = requests.get("https://api.semanticscholar.org/v1/paper/" + doi + "?include_unknown_references=true")
	time.sleep(2)
	if r.ok:
		return r.json()
	else:
		print("Error requesting metadata of doi " + doi)
		print(r)
		exit()

if not os.path.exists("../_data/papermetadata"):
	os.makedirs("../_data/papermetadata")

datapapers = []
with open("../_data/msrdatapapersperyear.json") as infile:
	datapapers = json.load(infile)

for year in datapapers:
	for paperdoi in datapapers[year]:
		paperid = "MSR" + year + "_" + "_".join(paperdoi.split("/"))
		print("Retrieving metadata for paper " + paperid)
		if not os.path.exists("../_data/papermetadata/" + paperid + ".json"): # paper metadata not already retrieved
			papermetadata = request_for_metadata(paperdoi)
			with open("../_data/papermetadata/" + paperid + ".json", 'w') as outfile:
				json.dump(papermetadata, outfile, indent=4)
		print("Metadata retrieved")

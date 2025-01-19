import os
import json
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

papers_and_datasets = {}
for paper in os.listdir('../_data/paperannotations'):
	paperid = paper[:-5]
	with open(os.path.join('../_data/paperannotations', paper)) as infile:
		papers_and_datasets[paperid] = json.load(infile)["dataset"]

profile = webdriver.FirefoxOptions()
profile.set_preference('browser.download.folderList', 2) # custom location
profile.set_preference('browser.download.manager.showWhenStarting', False)
profile.set_preference('browser.download.dir', '/tmp')
profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/json')
profile.add_argument("--headless")
browser = Firefox(profile)
for paperid, dataset_url in papers_and_datasets.items():
	if dataset_url != "-":
		assessmentfile = os.path.join("../_data/fairassessments", paper_id + ".json")
		if not os.path.exists(assessmentfile):
			print("Processing: " + dataset_url)
			try:
				browser.get('https://www.f-uji.net/index.php?action=test')
				search_form = browser.find_element('id', 'pid')
				search_form.send_keys(dataset_url)
				search_button = browser.find_element('name', 'runtest')
				search_button.click()
				elem = WebDriverWait(browser, 60).until(EC.element_to_be_clickable(('name', 'downloadtest')))
				result_button = browser.find_element('name', 'downloadtest')
				result_button.send_keys(Keys.RETURN) 
				print("Success!")
			except:
				print("Error downloading dataset")
			finally:
				browser.quit()
				profile = webdriver.FirefoxOptions()
				profile.set_preference('browser.download.folderList', 2) # custom location
				profile.set_preference('browser.download.manager.showWhenStarting', False)
				profile.set_preference('browser.download.dir', '/tmp')
				profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/json')
				profile.add_argument("--headless")
				browser = Firefox(profile)
browser.quit()


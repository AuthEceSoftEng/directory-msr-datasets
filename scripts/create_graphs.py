import os
import json
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt


""" Set the input and output paths """
input_path = "../_data"
save_to_disk = False # whether to save the results and graphs to disk or not
if save_to_disk:
	output_path = "../results"
	if not os.path.exists(output_path):
		os.makedirs(output_path)


""" Read data and create dataframe """
# Load all paper info
papers = {}
for paper in os.listdir(os.path.join(input_path, 'papermetadata')):
	paperid = paper[:-5]
	papers[paperid] = {}
	with open(os.path.join(input_path, 'papermetadata', paper)) as infile:
		papers[paperid]["metadata"] = json.load(infile)
	with open(os.path.join(input_path, 'paperannotations', paper)) as infile:
		papers[paperid]["annotations"] = json.load(infile)
	if os.path.exists(os.path.join(input_path, 'fairassessments', paper)):
		with open(os.path.join(input_path, 'fairassessments', paper)) as infile:
			papers[paperid]["fairassessment"] = json.load(infile)
# Create data frame
dfpaperdata = []
for paperid, paper in papers.items():
	dfpaperdata.append([paperid,
						paper["metadata"]["title"],
						paper["annotations"]["category"],
						paper["annotations"]["topic"],
						paper["metadata"]["year"],
						len(paper["metadata"]["citations"]),
						paper["annotations"]["dataset"] != "-",
						paper["fairassessment"]["summary"]["score_percent"]["FAIR"] if "fairassessment" in paper else None])
df = pd.DataFrame(dfpaperdata, columns = ["ID", "Title", "Category", "Topic", "Year", "Citations", "Dataset", "FAIRScore"])
#if save_to_disk:
#	df.to_csv(os.path.join(output_path, 'allresults.csv'), index = False, sep = ';')  


""" Set data and plot parameters """
years = list(sorted(df.Year.unique()))
categories = ["Version Control", "Software Issues", "Developer Metrics", "Software Evolution", "Semantic Metrics", "Other Data"]
topics = [str(t) for t in range(0, 14)]
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color = ["#7a7a9b", "#dcdcff"]) 


""" Number of papers and number of datasets """
# Find number of papers per year and number of datasets per year
totals, havedata = [], []
for year in years:
	dataforyear = df.loc[df.Year == year]
	totals.append(len(dataforyear))
	havedata.append(len(dataforyear.loc[df.Dataset == True]))
# Plot using a stacked bar plot
fig, ax = plt.subplots(figsize = (6.65, 3))
ax.bar([str(year) for year in years], havedata, label = "Data available")
ax.bar([str(year) for year in years], [t - h for h, t in zip(havedata, totals)], label = "Total papers", bottom = havedata)
ax.legend()
ax.set_xlabel("Years")
ax.set_ylabel("Number of papers")
plt.tight_layout()
if save_to_disk:
	plt.savefig(os.path.join(output_path, "papersperyear.pdf"))


""" Number of citations per paper """
# Plot the number of citations per paper
fig, ax = plt.subplots(figsize = (6.65, 3.36))
bins = np.arange(0, 106, 5)
plt.hist(np.clip(df.Citations, bins[0], bins[-1]), bins = bins, edgecolor = 'black', range = [0, 101], align = 'mid', rwidth = 1)
ax.set_xlabel("Number of citations")
ax.set_ylabel("Number of papers")
plt.xticks(np.arange(0, 101, 5) + 2.5, ["[%d,%d)" % (s, t) for s, t, in zip(np.arange(0, 96, 5), np.arange(5, 101, 5))] + ['[100,' + u'\u221E' + ')'], rotation = 45, ha = 'right')
plt.tight_layout()
if save_to_disk:
	plt.savefig(os.path.join(output_path, "citationsperpaper.pdf"))


""" Number of citations per category """
# Compute the number of datasets per category, the percentage per category, and the average number of citations
countcategories = []
countcitations = []
avgcitations = []
for category in categories:
	tempdf = df.loc[df.Category == category]
	countcategories.append(len(df.loc[df.Category == category]))
	countcitations.append(df.loc[df.Category == category].Citations)
	avgcitations.append(df.loc[df.Category == category].Citations.mean())
categories_dfrm = pd.DataFrame({"Dataset Category": categories,
								"Total number of datasets": countcategories,
								"Percentage of datasets": [round(100 * c / sum(countcategories), 4) for c in countcategories],
								"Average number of citations": [round(a) for a in avgcitations]})
print(categories_dfrm.to_string(index = False))
# Plot the number of citations per category
fig, ax = plt.subplots(figsize = (6.65, 3.21))
ax.boxplot(countcitations, patch_artist = True, labels = ["\n".join(c.split(" ")) for c in categories])
ax.set_ylim(0, 100)
ax.set_xlabel("Dataset category")
ax.set_ylabel("Number of citations")
plt.tight_layout()
if save_to_disk:
	plt.savefig(os.path.join(output_path, "citationspercategory.pdf"))


""" Number of citations per topic """
# Compute the number of datasets per topic, the percentage per topic, and the average number of citations
counttopics = []
countcitations = []
avgcitations = []
for topic in topics:
	tempdf = df.loc[df.Topic == topic]
	counttopics.append(len(df.loc[df.Topic == topic]))
	countcitations.append(df.loc[df.Topic == topic].Citations)
	avgcitations.append(df.loc[df.Topic == topic].Citations.mean())
topics_dfrm = pd.DataFrame({"Dataset Topic": topics,
								"Total number of datasets": counttopics,
								"Percentage of datasets": [round(100 * c / sum(counttopics), 4) for c in counttopics],
								"Average number of citations": [round(a) for a in avgcitations]})
print(topics_dfrm.to_string(index = False))


""" Average FAIR score per year """
# Plot FAIR score per year
df = df.dropna()
YearFAIRscore = []
for year in years:
	tempdf = df.loc[df.Year == year]
	YearFAIRscore.append(tempdf.FAIRScore.mean())
fig, ax = plt.subplots(figsize = (6.65, 3))
ax.bar([str(year) for year in years], YearFAIRscore)
ax.plot([str(year) for year in years], YearFAIRscore, 'k--')
ax.set_xlabel("Year")
ax.set_ylabel("Average FAIR score")
plt.tight_layout()
if save_to_disk:
	plt.savefig(os.path.join(output_path, "fairscoreperyear.pdf"))


""" FAIR score vs citations per year """
# Plot FAIR score vs citations
df = df.dropna()
fig, ax = plt.subplots(figsize = (6.65, 4))
bubbles = ax.scatter(df.Year, df.FAIRScore, s = np.clip(df.Citations, 0, 100) * 1.5, alpha = 0.5)
ax.set_xlabel("Year")
ax.set_ylabel("FAIR score")
ax.set_ylim(0, 88)
ax.set_xticks(years)
ax.set_xticklabels(years)
kw = dict(prop = "sizes", num = [10, 50, 100], color = "#7a7a9b")
legend = ax.legend(*bubbles.legend_elements(**kw), title = "Citations", edgecolor = "black",
					loc = 'upper left', bbox_to_anchor = (1, 1.02), labelspacing = 0.5, frameon = True)
plt.tight_layout()
if save_to_disk:
	plt.savefig(os.path.join(output_path, "fairscorecitations.pdf"))


plt.show()

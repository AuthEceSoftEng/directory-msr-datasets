import os
import re
import json
import nltk
try:
	from nltk.corpus import stopwords
except:
	nltk.download('stopwords')
	from nltk.corpus import stopwords
stop_words = stopwords.words('english')
stop_words.extend(['dataset', 'data', 'software', 'research', 'researchers', 'open', 'available', 'used', 'paper'])
from gensim.corpora import Dictionary
from gensim.utils import simple_preprocess
from gensim.models import LdaModel, CoherenceModel
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['axes.prop_cycle'] = mpl.cycler(color = ["#7a7a9b", "#dcdcff"]) 

# Function used for text preprocessing
def preprocess_text(text):
	text = re.sub('\s+', ' ', text)  # remove extra spaces
	text = re.sub('\S*@\S*\s?', '', text)  # remove emails
	text = re.sub('\'', '', text)  # remove apostrophes
	text = re.sub('[^a-zA-Z]', ' ', text)  # remove non-alphabet characters
	text = text.lower()  # convert to lowercase
	return text

# Function used for tokenization and stopwords removal
def tokenize(text):
	tokens = simple_preprocess(text, deacc=True)
	tokens = [token for token in tokens if token not in stop_words]
	return tokens

# Function used for lemmatization
def lemmatize(tokens):
	return [lemmatizer.lemmatize(token) for token in tokens]

if __name__ == "__main__":
	# Load all paper abstracts
	with open("../_data/msrdatapapersperyear.json") as infile:
		datapapers = json.load(infile)
	paperids, paperabstracts = [], []
	for year in datapapers:
		for paperdoi in datapapers[year]:
			paperid = "MSR" + year + "_" + "_".join(paperdoi.split("/"))
			paperids.append(paperid)
			with open("../_data/papermetadata/" + paperid + ".json", 'r') as infile:
				papermetadata = json.load(infile)
			paperabstracts.append(papermetadata["abstract"])

	# Preprocess texts
	texts = []
	for paperabstract in paperabstracts:
		text = preprocess_text(paperabstract)
		text = tokenize(text)
		text = lemmatize(text)
		texts.append(text)

	# Create dictionary
	id2word = Dictionary(texts)
	id2word.filter_extremes(no_below = 5, no_above = 0.8)
	corpus = [id2word.doc2bow(text) for text in texts]

	# Find coherences to determine optimal number of topics
	if not os.path.exists("../_data/topicmodeling/topicmodelingcoherences.json"):
		coherences = {}
		for num_topics in range(5, 21):
			lda_model = LdaModel(corpus = corpus, id2word = id2word, num_topics = num_topics, random_state = 24)
			coherence_model = CoherenceModel(model = lda_model, texts = texts, dictionary = id2word, coherence = 'c_v')
			coherence_score = coherence_model.get_coherence()
			coherences[num_topics] = coherence_score
			print("\n\n\n%d TOPICS" % num_topics)
			print(coherence_score)
			for topic in lda_model.print_topics(num_topics = 20, num_words = 10):
				print(topic)
		# Save coherences to disk
		with open("../_data/topicmodeling/topicmodelingcoherences.json", 'w') as outfile:
			json.dump(coherences, outfile, indent = 4)
	else:
		# Load coherences from disk
		with open("../_data/topicmodeling/topicmodelingcoherences.json") as infile:
			coherences = json.load(infile)
	# Plot coherences
	x_val, y_val = zip(*sorted([(int(k), v) for k, v in coherences.items()]))
	fig, ax = plt.subplots(figsize = (6.65, 3))
	ax.plot(x_val, y_val)
	ax.scatter(x_val, y_val)
	ax.set_xlabel('Number of Topics')
	ax.set_ylabel('Coherence')
	ax.set_xticks(x_val)
	plt.tight_layout()
	#plt.savefig("../_data/topicmodeling/topicmodelingcoherences.pdf")
	#plt.show()

	# Apply topic modeling for the optimal number of topics (14)
	if not os.path.exists("../_data/topicmodeling/ldamodel"):
		lda_model = LdaModel(corpus = corpus, id2word = id2word, num_topics = 14, random_state = 24)
		lda_model.save("../_data/topicmodeling/ldamodel")
	else:
		lda_model = LdaModel.load("../_data/topicmodeling/ldamodel")
	for topic in lda_model.print_topics(num_topics = 14, num_words = 10):
		print(topic)

	# Save topics to disk (top 10 terms)
	with open("../_data/topicmodeling/topics_terms.json", 'w') as outfile:
		topics_terms = {}
		for t, topic in lda_model.show_topics(num_topics = 14, formatted = False, num_words = 10):
			topics_terms["topic" + str(t)] = [word[0] for word in topic]
		json.dump(topics_terms, outfile, indent = 4)

	# Save best topic (top 10 terms) for each document to disk
	with open("../_data/topicmodeling/topics_abstracts.json", 'w') as outfile:
		topics_abstracts = {}
		for paperid, paperabstract in zip(paperids, corpus):
			#print(lda_model[paperabstract])
			best_topic = list(sorted(lda_model[paperabstract], key=lambda x: x[1]))[-1][0]
			#print(best_topic)
			topics_abstracts[paperid] = str(best_topic) #topics_terms["topic" + str(best_topic)]
		json.dump(topics_abstracts, outfile, indent = 4)

	# Update paper annotations
	for paper in os.listdir('../_data/paperannotations'):
		paperid = paper[:-5]
		with open(os.path.join('../_data/paperannotations', paper)) as infile:
			paperannotations = json.load(infile)
			paperannotations["topic"] = topics_abstracts[paperid]
			paperannotations["topicTerms"] = topics_terms["topic" + topics_abstracts[paperid]]
			#print(paperannotations)
		with open(os.path.join('../_data/paperannotations', paper), 'w') as outfile:
			json.dump(paperannotations, outfile, indent = 4)

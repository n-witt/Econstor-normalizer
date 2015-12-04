from gensim import corpora, models, similarities
import logging
import os
import json
import cPickle as pickle
from collections import defaultdict 

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
workingDir = u'cache'
documentsFile = workingDir + os.sep + u'documentMatrix'
dictFile = workingDir + os.sep + u'econstor.dict'
corpusFile = workingDir + os.sep + u'corpus.mm'

def langFilteredFiles(files, lang=u'en'):
    for file in files:
        with open(file) as f:
            document = json.loads(f.read())
            if document[u'lang'] == u'en':
                yield document

def readFiles(folder):
    files = os.listdir(folder)
    files = [folder + os.sep + file for file in files]
    for file in langFilteredFiles(files):
        yield file[u'plaintext']
            
def getDocumentMatrix(documentsFile):
    # create document vectors
    if not os.path.exists(documentsFile):
        logging.info(u'Creating document matrix file ')
        for document in readFiles('samples'):
            documents.append(document)
        # remove stop words    
        stoplist = set("for he she it a of the and to in".split())
        texts = [[token for token in document.lower().split() if token not in stoplist]
                for document in documents]
        
        # remove word that occur once
        frequency = defaultdict(int)
        for text in texts:
            for token in text:
                frequency[token] += 1
        texts = [[token for token in text if frequency[token] > 1]
                 for text in texts]
        logging.info(u'Document matrix created.')
        with open(documentsFile, "wb") as f:
            pickle.dump(texts, f)
            logging.info(u'Document matrix written.')
    else:
        with open(documentsFile, "rb") as f:
            texts = pickle.load(f)
            logging.info(u'Document matrix loaded.')
    return texts

def getDictionary(dictFile):
    # create or read the dictionary
    if not os.path.exists(dictFile):
        logging.info(u'Building dictionary.')
        # create dictionary
        texts = getDocumentMatrix(documentsFile)
        dictionary = corpora.Dictionary(texts)
        dictionary.save(dictFile)
        logging.info(u'Dictionary written')
    else:
        dictionary = corpora.Dictionary.load(dictFile)
        logging.info(u'Dictionary loaded.')
    return dictionary

def getCorpus(corpusFile):
    # create or read the corpus
    if not os.path.exists(corpusFile):
        logging.info(u'Building corpus.')
        dictionary = getDictionary(dictFile)
        texts = getDocumentMatrix(documentsFile)
        corpus = [dictionary.doc2bow(text)for text in texts]
        corpora.MmCorpus.serialize(corpusFile, corpus)
        logging.info(u'Corpus written.')
    else:
        corpus = corpora.MmCorpus(corpusFile)
        logging.info(u'Corpus loaded.')
    return corpus

if __name__ == '__main__':
    documents = []
    
    if not os.path.exists(workingDir):
        os.mkdir(workingDir)
    
    # create tf-idf transformation
    corpus = getCorpus(corpusFile)
    dict = getDictionary(dictFile)
    tfidf = models.TfidfModel(corpus)
    
    tfidfCorpus =  [tfidf[d] for d in corpus]
    
    lsi = models.LsiModel(tfidfCorpus, id2word=dict, num_topics=3)
    lsi.print_topics(3)
    lsiCorpus = lsi[tfidfCorpus]
    
    index = similarities.MatrixSimilarity(lsiCorpus)
    
    print(corpus)
    
import time
import os
from pdfLib import PdfLib
import langdetect
from filter import Filter
import json
from googleScholar import *
from fuzzywuzzy import fuzz

class ProcessWorker():
    def __init__(self, filename, wd, od, logger, uq, fileExtension = u'.json'):
        """
        wd    -> working dir
        od    -> output dir
        uq    -> update queue
        """
        self.logger = logger
        self.filename = filename
        self.wd = wd
        self.od = od
        self.uq = uq
        self.fileExtension = fileExtension
        self.outFilename = self.filename + self.fileExtension
        
        self.langKey = u'lang'
        self.plaintextKey = u'plaintext'
        self.filenameKey = u'filename'
        
    def process_data(self):
        """
        This method is the entry point for the worker processes
        """
        i = 0
        self.logger.info(u"start processing {}.".format(self.filename))
        start = time.time()
        content = {}
        try:
            content = self.__loadFile()

            if content.has_key(self.plaintextKey) and \
            content.has_key(self.langKey) and \
            content.has_key(self.filenameKey):
                # does the file already have all the properties we want 
                # to create? if so, let's assume the file has already been
                # processed and skip it
                self.logger.warning(u"{} not written. Information already present. skipped".format(self.outFilename))
                self.uq.put(('complete', self.filename))
                return

            # create or update the file with the new information
            result = self.__getPlaintext()
            citationCount = self.__getCitationCount()
            with open(self.od + os.sep + self.outFilename, "w+") as f:
                content.update(result)
                content['citationCount'] = citationCount
                f.write(json.dumps(content).decode("utf8"))
                self.uq.put(('complete', self.filename))
                
        except Exception as e:
            self.logger.error(unicode(e))
            self.uq.put(('broken', self.filename, e.message))
        stop = time.time()
        self.logger.info(u"Took {:.2f}s.".format(stop-start))
        i += 1
    
    '''
    gets plaintext from file at path "self.filename", does some normalization
    and saves it into "outfile".
    '''
    def __getPlaintext(self):
        # extract plaintext from pdf
        paper = PdfLib(self.wd + os.sep + self.filename)
        textBeginning = self.__guessDocBegining(self.filename)
        plaintext = paper.pdf2txt(textBeginning, "max")
        
        # normalize text
        f = Filter(asString=plaintext)
        plaintext = f.substitutions() \
            .oneCharPerLine() \
            .normalizeCaracters() \
            .lower() \
            .uselessCharacters() \
            .multipleDots() \
            .listEnum() \
            .digits() \
            .shortTokens() \
            .multipleSpaces() \
            .getResult()   
        
        # experience shows, that less than 6000 characters is mostly waste
        if len(plaintext) > 6000:
            result = {}
            result[self.langKey] = self.__guessLang(plaintext)
            result[self.plaintextKey] = plaintext
            result[self.filenameKey] = self.filename
            return result
        else:
            raise Exception(u"Document is too short.")
        
    def __persist(self, text, filename):
        with open(filename, "w") as f:
            f.write(json.dumps(text).encode("utf8"))
        self.logger.info(u"{} written.".format(filename))
        
    
    def __guessDocBegining(self, filename):
        if os.path.exists(self.wd + os.sep + filename):
            """
            inspect the first 5 pages. when a page consists of more than 1500 characters,
            assume this is the beginning of the text. Those values are based on experience,
            not science ;)
            """
            maxPages = 5
            threshold = 1300
            for p in range(1, maxPages):
                paper = PdfLib(self.wd + os.sep + filename)
                text = paper.pdf2txt(p)
                numChar = len(text)
                textLower = text.lower()
                if numChar > threshold or textLower.find("abstract") != -1 or textLower.find("introduction") != -1:
                    return p
            return maxPages
        else:
            self.logger.info(u"{} does not exist.".format(filename))
        
    def __guessLang(self, text):
        return langdetect.detect(text)
    
    def __loadFile(self):
        with open(self.od + os.sep + self.outFilename, "r") as f:
            return json.loads(f.read())
    
    def __getCitationCount(self, sep="|"):
        content = self.__loadFile()
        
        # <initializing googleScholar.py>
        querier = ScholarQuerier()
        settings = ScholarSettings()
        querier.apply_settings(settings)
        query = SearchScholarQuery()
        # this is the actual query text
        query.set_words(content['title'])
        # search for title only
        query.set_scope(True)
        querier.send_query(query)
        # </initializing googleScholar.py>
        
        result = csv(querier, header=True, sep=sep) # result[0] first row (headlines), result[1] second row (first data row), ...
        if result == None:
            self.logger.info(u"#### zero citations ####")
            return 0
        
        # csv to list of dicts like:
        # [{'title': 'Highway to Hitler', ....}, {'title': '<some other title>'}]
        intermediate = [a.split(sep) for a in result.split("\n")]
        final = [{intermediate[0][i]: w  for i, w in enumerate(t)} \
                 for t in intermediate[1:]]
        
        # count citations
        citations = 0
        for d in final:
            # only count if titles are sufficiently similar
            # see https://github.com/seatgeek/fuzzywuzzy for details 
            if fuzz.token_set_ratio(d['title'], content['title']) >= 85:
                if d.has_key('num_citations'):
                    if type(d['num_citations']) == int:
                        citations += d['num_citations']
                    elif type(d['num_citations']) == unicode or type(d['num_citations']) == str:
                        try:
                            citations += int(d['num_citations'])
                        except ValueError:
                            pass
        return citations
                
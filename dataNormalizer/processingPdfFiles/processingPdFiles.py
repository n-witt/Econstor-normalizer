import time
import os
from processingPdfFiles.pdfTools.pdfLib import PdfLib
import langdetect
from  processingPdfFiles.filter import Filter
import json

class ProcessWorker():
    def __init__(self, filename, wd, od, logger, eq, fileExtension = u'.json'):
        """
        wd    -> working dir
        od    -> output dir
        er    -> error queue
        """
        self.logger = logger
        self.filename = filename
        self.wd = wd
        self.od = od
        self.eq = eq
        self.fileExtension = fileExtension
        
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
            outFilename = self.filename + self.fileExtension 
            if os.path.exists(self.od + os.sep + outFilename):
                with open(self.od + os.sep + outFilename, "r") as f:
                    content = json.loads(f.read())
                
                if content.has_key(self.plaintextKey) and \
                    content.has_key(self.langKey) and \
                    content.has_key(self.filenameKey):
                    # does the file already have all the properties we want 
                    # to create? if so, let's assume the file has already been
                    # processed and skip it
                    self.logger.warning(u"{} not written. Information already present. skipped".format(outFilename))
                    return
                    
            # create or update the file with the new information
            result = self.__getPlaintext()
            with open(self.od + os.sep + outFilename, "w+") as f:
                content.update(result)
                f.write(json.dumps(content).decode("utf8"))
                
        except Exception as e:
            self.logger.error(unicode(e))
            self.eq.put((self.filename, e))
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
        f = Filter(plaintext)
        plaintext = f.normalizeCaracters() \
            .remOneCharPerLine() \
            .filterCharacters() \
            .multipleSpaces() \
            .multipleDots() \
            .listEnum() \
            .getResult()
        
        # experience shows, that less than 6000 characters is mostly waste
        if plaintext.__len__() > 6000:
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
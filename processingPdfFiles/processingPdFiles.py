import time
import os
from processingPdfFiles.pdfTools.pdfLib import PdfLib
import langdetect
from  processingPdfFiles.filter import Filter
import json

class ProcessWorker():
    def __init__(self, filename, wd, od, logger, eq):
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
        
    def process_data(self):
        """
        This method is the entry point for the worker processes
        """
        i = 0
        self.logger.info(u"start processing {}.".format(self.filename))
        start = time.time()
        try:
            outFilename = self.filename + u".json" 
            if not os.path.exists(self.od + os.sep + outFilename):
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
                    result["lang"] = self.__guessLang(plaintext)
                    result["plaintext"] = plaintext
                    result["filename"] = self.filename
                    fd = open(self.od + os.sep + outFilename, "w")
                    fd.write(json.dumps(result).encode("utf8"))
                    fd.close()
                    self.logger.info(u"{} written.".format(outFilename))
                else:
                    raise Exception(u"{} was not written. Document is too short.".format(outFilename))
            else:
                self.logger.info(u"Failed to write {}. File already exists.".format(outFilename))
        except Exception as e:
            self.logger.warn(unicode(e))
            self.eq.put((self.filename, e))
        stop = time.time()
        self.logger.info(u"Took {:.2f}s.".format(stop-start))
        i += 1
            
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
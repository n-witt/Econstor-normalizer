import time
import os
from processingPdfFiles.pdfTools.pdfLib import PdfLib
import langdetect
from  processingPdfFiles.filter import Filter

class ProcessWorker():
    def __init__(self, pName, l, wd, od, logger, eq):
        """
        pName -> process name
        l     -> list of filenames
        wd    -> working dir
        od    -> output dir
        er    -> error queue
        """
        self.logger = logger
        self.pName = pName
        self.l = l
        self.wd = wd
        self.od = od
        self.eq = eq
        
    def process_data(self):
        """
        This method is the entry point for the worker processes
        """
        self.logger.info(u"Starting " + self.pName) 
        i = 0
        for filename in self.l:
            self.logger.info(u"[{}] start processing {}.".format(self.pName, filename))
            start = time.time()
            try:
                plainFilename = filename + u".txt" 
                if not os.path.exists(self.od + os.sep + plainFilename):
                    # extract plaintext from pdf
                    paper = PdfLib(self.wd + os.sep + filename)
                    textBeginning = self.__guessDocBegining(filename)
                    plaintext = paper.pdf2txt(textBeginning, "max")
                     
                    lang = self.__guessLang(plaintext)
                    
                    # normalize text
                    f = Filter(plaintext)
                    plaintext = f.remOneCharPerLine() \
                        .filterCharacters() \
                        .multipleSpaces() \
                        .multipleDots() \
                        .listEnum() \
                        .normalizeCaracters() \
                        .getResult() \
                    
                    fd = open(self.od + os.sep + lang + u"_" + plainFilename, "w")
                    fd.write(plaintext.encode("utf-8"))
                    fd.close()
                    
                    self.logger.info(u"[{}]   {} written.".format(self.pName, plainFilename))
                else:
                    self.logger.info(u"[{}]    Failed to write {}. File already exists.".format(self.pName, plainFilename))
            except Exception as e:
                self.logger.warn(str(e))
                self.eq.put((filename, e))
                continue
            stop = time.time()
            self.logger.info(u"[{}]   {:.2f} % complete. Took {:.2f}s.".format(self.pName, (float(i)/len(self.l))*100, stop-start))
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
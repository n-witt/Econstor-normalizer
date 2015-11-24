import time
import os
from processingPdfFiles.pdfTools.pdfLib import PdfLib 

class ProcessWorker():
    def __init__(self, pName, l, wd, od, logger):
        """
        pName -> process name
        l     -> list of filenames
        wd    -> working dir
        od    -> output dir
        """
        self.logger = logger
        self.pName = pName
        self.l = l
        self.wd = wd
        self.od = od
        
        
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
                    paper = PdfLib(self.wd + os.sep + filename)
                    textBeginning = self.__guessDocBegining(filename) 
                    plaintext = paper.pdf2txt(textBeginning, "max")
                    fd = open(self.od + os.sep + plainFilename, "w+")
                    fd.write(plaintext)
                    self.logger.info(u"   [{}] {} written.".format(self.pName, plainFilename))
                else:
                    self.logger.info(u"   [{}] Failed to write {}. File already exists.".format(self.pName, plainFilename))
            except Exception as e:
                self.logger.warn(str(e))
                continue
            stop = time.time()
            self.logger.info(u"   [{}] {:.2f} % complete. Took {:.2f}s.".format(self.pName, (float(i)/len(self.l))*100, stop-start))
            i += 1
            
    def __guessDocBegining(self, filename):
        if os.path.exists(filename):
            """
            inspect the first 5 pages. when a page consists of more than 1300 characters,
            assume this is the beginning of the text. Those values are based on experience,
            not science ;)
            """
            maxPages = 5
            threshold = 1300
            for p in range(maxPages):
                text = PdfLib.pdf2txt(self.wd + os.sep + filename, p)
                numChar = len(text)
                if numChar > threshold:
                    return p
            return maxPages
        else:
            self.logger.info(u"{} does not exist.".format(filename))
        
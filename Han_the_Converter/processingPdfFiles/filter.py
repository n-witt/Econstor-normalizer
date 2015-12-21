import os
import codecs
import unicodedata
import re

class Filter():
    def __init__(self, asFile='', asString=''):
        if os.path.exists(asFile):
            # let's assume that s is a path
            fd = codecs.open(asFile, "r", "utf8")
            self.s = fd.read()
            fd.close()
        elif asString != '':
            self.s = asString
        else:
            raise IOError("file not found")
            
    def normalizeCaracters(self):
        '''
        converts 'ueber' to 'uber'
        ''' 
        self.s = unicodedata.normalize("NFKD", self.s).encode("ascii", "ignore").decode("utf8")
        return self
    
   
    def oneCharPerLine(self):
        """
        transforms "\nF\n\O\nO" to "FOO".
        OCPL -> one character per line
        """
        self.s = "".join(self.s.split("\n"))
        # "fooBar" -> "foo Bar"
        self.s = re.sub(r'([a-z])([A-Z0-9])', r'\1 \2', self.s)
        return self
    
    def uselessCharacters(self):
        """
        Lets pass only meaningful characters 
        """
        self.s = re.sub(r'([^a-zA-Z0-9 \.,_;:%\?!])', '', self.s)
        return self
    
    def listEnum(self):
        """
        removes list enumarations s.a. "2.1.3 topic x"
        """
        re.sub(r'([0-9]*\.[0-9]*)', '', self.s)
        return self
    
    def multipleDots(self):
        # removes multiple dots with optional whitespaces in between
        self.s = re.sub(r'((\.\s*){2,})', '', self.s)
        return self
    
    def multipleSpaces(self):
        """
        Removes multiple whitespaces  
        """
        self.s = re.sub(r'(\s{2,})', ' ', self.s)
        return self
    
    def lower(self):
        # lowercases everything
        self.s = self.s.lower()
        return self
    
    def shortTokens(self):
        # removes tokens shorter than minLen
        self.s = re.sub(r'(?<=\s)[\w?!%,.;:\/]{1,3}(?=\s|\Z)', '', self.s)
        return self
        
    def digits(self):
        # removes all digits except digits that represent years
        self.s = re.sub(r'\b(?!(\D\S*|[12][0-9]{3})\b)\S+\b', '', self.s)
        return self
    
    def substitutions(self):
        # there are some cases where pdf miner produces garbage that
        # can be replaced with useful or less harmful thing.
        
        # replace '(cid:133)' with 'fi'.
        self.s = re.sub(r'\(cid:133\)', 'fi', self.s)
        
        # remove '(cid:<some number>')
        self.s = re.sub(r'\(cid:[0-9]*\)', '', self.s)
        
        # remove control characters
        self.s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', self.s)
        return self
        
    
    def getResult(self):
        return self.s

if __name__ == "__main__":
    f = Filter(u"../data/completedSamples/de_726720712.pdf.txt")
    res = f.normalizeCaracters() \
            .oneCharPerLine() \
            .uselessCharacters() \
            .digits() \
            .multipleDots() \
            .multipleSpaces() \
            .listEnum() \
            .lower() \
            .shortWords() \
            .getResult()
    print res
    

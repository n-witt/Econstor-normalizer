import os
import codecs
import unicodedata
import re

class Filter():
    def __init__(self, s):
        if os.path.exists(s):
            # let's assume that s is a path
            fd = codecs.open(s, "r", "utf8")
            self.s = fd.read()
            fd.close()
        else:
            self.s = s
            
    def normalizeCaracters(self):
        '''
        converts 'ueber' to 'uber'
        ''' 
        self.s = unicodedata.normalize("NFKD", self.s).encode("ascii", "ignore").decode("utf8")
        return self
    
   
    def remOneCharPerLine(self):
        """
        transforms "\nF\n\O\nO" to "FOO".
        OCPL -> one character per line
        """
        self.s = "".join(self.s.split("\n"))
        # "fooBar" -> "foo Bar"
        self.s = re.sub(r'([a-z])([A-Z0-9])', r'\1 \2', self.s)
        return self
    
    def filterCharacters(self):
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
        self.s = re.sub(r'(\.{2,})', ' ', self.s)
        return self
    
    def multipleSpaces(self):
        """
        Removes multiple whitespaces  
        """
        self.s = re.sub(r'(\s{2,})', ' ', self.s)
        return self
    
    def getResult(self):
        return self.s

if __name__ == "__main__":
    f = Filter(u"../data/txts/de_726720712.pdf.txt")
    res = f.normalizeCaracters().remOneCharPerLine().filterCharacters().multipleSpaces().multipleDots().listEnum().getResult()
    
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO
import os

"""
A library providing numerous methods to access information of reasearch papers.
It operates only on pdf-files 
"""
class PdfLib:
    
    def __init__(self, filename):
        if os.path.exists(filename) and filename.lower().endswith(".pdf"):
            self.filename = filename
        else:
            raise Exception(filename + " does not exists or is not a pdf file")
    
    def pdf2txt(self, lowerBorder=-1, upperBorder=-1):
        """
        Returns the plain text of the document. If lowerBorder is an int number > -1, only
        page referring to this number will be returned. If lowerBorder and upperBorder are >-1
        and upperBorder > lowerBoder, the pages referring to that range will be returned.  
        """
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        fp = file(self.filename, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        if (lowerBorder==-1 and upperBorder==-1) or (lowerBorder>-1 and upperBorder=="max"):
            pagenos=set()
        elif lowerBorder > -1 and upperBorder==-1:
            #extract only a single page
            pagenos=set(range(lowerBorder, lowerBorder+1))
        elif lowerBorder==-1 or upperBorder==-1 or lowerBorder > upperBorder:
            raise ValueError("illegal parameter passed")
        else:
            pagenos=set(range(lowerBorder, upperBorder+1))

        for (pageno, page) in enumerate(PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True)):
            if pageno < lowerBorder and upperBorder == "max":
                continue
            interpreter.process_page(page)
        fp.close()
        device.close()
        s = retstr.getvalue()
        retstr.close()
        #return s.decode('utf-8')
        return s
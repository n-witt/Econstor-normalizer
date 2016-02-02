# EconstorCorpus

[Econstor](https://www.econstor.eu/) is [ZBW](http://www.zbw.eu/)'s [Open access](https://en.wikipedia.org/wiki/Open_access) server for scientific publications. The software in this repository deals with the task of building a textmining corpus from EconStor documents.

# Overview
You can find two independent (yet related) components, that are described in the following:

## Luke the Downloader
  1. Generates an index of all EconStor files using the [Econbiz API](https://api.econbiz.de/doc)
  2. Downloads PDF files
  3. Determines RePEc handles for the documents
  4. Fetches citation count figures (using [CitEc](http://citec.repec.org/))

## Han the Converter
  1. Extracts plaintext from PDF files
  2. Guesses the language of the document
  3. Normalizes the plaintext (This may require tailoring for your purposes). [Details](https://github.com/n-witt/EconstorCorpus/blob/master/Han_the_Converter/processingPdfFiles/filter.py)

More information is provided in the IPython notebooks and README files in the subdirectories.

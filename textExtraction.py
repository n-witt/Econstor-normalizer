'''
Created on 19.11.2015

@author: nils witt
'''
import multiprocessing as mp
import os
from pdfTools import pdf2text
import logging

logging.getLogger().setLevel(logging.INFO)
numProcesses = mp.cpu_count()
processList = []
#for i in range(numProcesses/2):
for i in range(1):
    processList.append(("Process-" + str(i), i))
workingDir = "data/files"
outputDir = "data/txts"
processes = []

def process_data(pName, l, wd, od):
        print "Starting " + pName 
        i = 0
        for filename in l:
            try:
                plainFilename = filename + ".txt" 
                if not os.path.exists(od + os.sep + plainFilename):
                    plaintext = pdf2text.convert_pdf_to_txt(wd + os.sep + filename)
                    fd = open(od + os.sep + plainFilename, "w+")
                    fd.write(plaintext)
                    logging.info("[" + pName + "] " + plainFilename + " written. " + str((float(i)/len(l))*100) + "% complete.")
                else:
                    logging.info("Failed to write " + plainFilename + ". File already exists.")
            except Exception as e:
                logging.warn(str(e))
                continue
            i += 1

def fillLists(path, numChunks):
    if os.path.exists(path):
        docs = os.listdir(path)
        l = []
        lol = []
        for doc in docs:
            l.append(doc) 
        for i in range(numChunks):
            lol.append(l[i::numChunks])
        
        return lol
    else:
        raise Exception("path was not a valid path")

if __name__ == "__main__":
    
    l = fillLists(workingDir, numProcesses)
    # Create new threads
    for process in processList:
        arguments = (process[0], l[process[1]], workingDir, outputDir)
        p = mp.Process(target=process_data, args=arguments)
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
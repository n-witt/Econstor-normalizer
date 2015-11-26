'''
Created on 19.11.2015

@author: nils witt
'''
import multiprocessing as mp
import os
import logging
from processingPdfFiles.processingPdFiles import ProcessWorker

def errorHandler(q, f):
    while True:
        msg = q.get()
        if msg == "terminate!":
            break
        fd = open(f, "a")
        es = unicode(msg[0]) + u": " + unicode(msg[1]) + u"\n"
        fd.write(es.encode("utf8"))
        fd.close()

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
    
    logging.getLogger().setLevel(logging.INFO)
    numProcesses = mp.cpu_count()
    workingDir = u"../data/pdf"
    outputDir = u"../data/txts"
    errorOutputFile = u"../data/brokenPDFs"
    processes = []
    processList = []
    errorQueue = mp.Queue()

    # craft process's meta data
    for i in range(numProcesses):
    #for i in range(1):
        processList.append(("Process-" + str(i), i))

    # create numProcesses lists of file names from workingDir 
    l = fillLists(workingDir, numProcesses)

    # start errorHandling process    
    ep = mp.Process(target=errorHandler, args=(errorQueue, errorOutputFile))
    ep.start()
    
    # Create worker processes
    for process in processList:
        pw = ProcessWorker(process[0], l[process[1]], workingDir, outputDir, logging, errorQueue)
        p = mp.Process(target=pw.process_data, args=())
        p.start()
        processes.append(p)

    
    for p in processes:
        p.join()
    
    errorQueue.put("terminate!")
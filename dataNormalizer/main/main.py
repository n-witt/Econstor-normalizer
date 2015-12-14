'''
Created on 19.11.2015

@author: nils witt
'''
import multiprocessing as mp
import os
import logging
from processingPdfFiles.processingPdFiles import ProcessWorker
import time
from _socket import timeout

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
    
def isBrokenFile(filename, brokenFilesFile):
    if not os.path.exists(brokenFilesFile):
        return False
    else:
        with open(brokenFilesFile, u'r') as f:
            return f.read().find(filename) > -1 
    

if __name__ == "__main__":
    
    logging.getLogger().setLevel(logging.INFO)
    numProcesses = mp.cpu_count()
    workingDir = u"../data/pdf"
    outputDir = u"../data/txts"
    errorOutputFile = u"../data/brokenPDFs"
    fileExtension = u'.json'
    processes = []
    errorQueue = mp.Queue()
    filenames = []
    # protocol keeps track of the status of the files ('pending', 'broken', 'complete'=
    protocol = {'pending': [], 'broken': [], 'complete': []}
    
    # the time in seconds before a worker thread is being killed
    timeout = 600.0

    # create list of all files in `workingDir`
    if os.path.exists(workingDir):
        docs = os.listdir(workingDir)
        for doc in docs:
            filenames.append(doc) 
    else:
        raise Exception("path was not a valid path")

    # start errorHandling process    
    ep = mp.Process(target=errorHandler, args=(errorQueue, errorOutputFile))
    ep.start()
    
    numFiles = len(filenames)
    while len(filenames) > 0:
        if len(processes) <= numProcesses:
            filename = filenames.pop()
            if not isBrokenFile(filename, errorOutputFile):
                pw = ProcessWorker(filename, workingDir, outputDir, logging, errorQueue, fileExtension)
                p = mp.Process(target=pw.process_data, args=())
                p.start()
                processes.append((p, time.time(), filename))
        else:
            time.sleep(1)
            for process in processes:
                if process[0].is_alive():
                    now = time.time()
                    if now - process[1] > timeout:
                        process[0].terminate()
                        processes.remove(process)
                        errString = u'{} ran into timeout'.format(process[2])
                        logging.info(errString)
                        errorQueue.put((process[2], Exception(errString)))
                else:
                    processes.remove(process)
        logging.info(u'{:.2f}% completed'.format((1 - (len(filenames)/float(numFiles)))*100))
    
    for p in processes:
        p.join()
    
    errorQueue.put("terminate!")

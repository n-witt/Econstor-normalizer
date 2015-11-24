'''
Created on 19.11.2015

@author: nils witt
'''
import multiprocessing as mp
import os
import logging
import processingPdfFiles

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
    processes = []
    processList = []

    # craft process's meta data
    #for i in range(numProcesses/2):
    for i in range(1):
        processList.append(("Process-" + str(i), i))

    # create numProcesses lists of file names from workingDir 
    l = fillLists(workingDir, numProcesses)
    
    # Create new processes
    for process in processList:
        pw = processingPdfFiles.ProcessWorker(process[0], l[process[1]], workingDir, outputDir, logging)
        p = mp.Process(target=pw.process_data, args=())
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
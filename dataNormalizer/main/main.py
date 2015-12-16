'''
Created on 19.11.2015

@author: nils witt
'''
import multiprocessing as mp
import threading
import os
import logging
from processingPdfFiles.processingPdFiles import ProcessWorker
import time
# import pickle as pickle
import pickle as pickle

class journalHandler(object):
    def __init__(self, pendingQ, updateQ, waitForResume, workingDir):
        # restricts access to the journal object. this is crucial for pickling
        self.journalLock = threading.Lock()
        pickleFile = u'../data/journal.pickle'
        # in seconds
        pickleInterval = 30.0
        
        # read pickled journal if exists. create list of files otherwise
        try:
            with open(pickleFile, 'r') as pf:
                with self.journalLock:
                    journal = pickle.load(pf)
        except IOError:
            # create list of all files in `workingDir`
            if os.path.exists(workingDir):
                # journal keeps track of the status of the files ('pending', 'broken', 'complete')
                with self.journalLock:
                    journal = {'pending': {}, 'broken': {}, 'complete': {}}
                docs = os.listdir(workingDir)
                for doc in docs:
                    with self.journalLock:
                        journal['pending'][doc] = '' 
            else:
                raise Exception("working dir doesn't exist")        
        
        # expose list of files to main process 
        with self.journalLock:
            for f in journal['pending']:
                pendingQ.put(f)
        
        # tell release waiting processes that are waiting for the list of files 
        waitForResume.put('done')
            
        # handle updates to journal
        t = threading.Thread(target=self.__handlejournalUpdates, args=(journal, updateQ));
        t.start()

        # pickle list periodically
        while not pendingQ.empty():
            time.sleep(pickleInterval)
            with self.journalLock:
                with open(pickleFile, "wb") as f:
                    pickle.dump(journal, f)
            numDocuments = len(journal['complete']) + len(journal['broken']) + len(journal['pending'])
            logging.info("\n\n### STATUS ###\njournal pickled. stats:\ncomplete: {}\nbroken: {}\npending: {}\nsum: {}\ncomplete: {:.2f}%\n".format( \
                len(journal['complete']), \
                len(journal['broken']), \
                len(journal['pending']), \
                numDocuments, \
                (1 - len(journal['pending'])/float(numDocuments))*100))

        with self.journalLock:
            with open(pickleFile, "wb") as f:
                pickle.dump(journal, f)
        
        # kill the thread
        updateQ.put(('terminate'))
        t.join(10)
        return
    
    def __handlejournalUpdates(self, journal, updateQ):
        for item in self.__getItem(updateQ):
            with self.journalLock:
                if item[0] == 'complete':
                    # remove from 'pending' list
                    journal['pending'].pop(item[1])
                    # insert into 'complete' list
                    journal['complete'][item[1]] = ''
                elif item[0] == 'broken':
                    # remove from 'pending' list
                    journal['pending'].pop(item[1])
                    # insert into 'broken' list and store error msg
                    journal['broken'][item[1]] = item[2]
                else:
                    logging.error("invalid journal message received")

    def __getItem(self, updateQ):
        while True:
            item = updateQ.get()
            if item == 'terminate':
                break
            yield item

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
    workingDir = u'../data/pdf'
    outputDir = u"../data/json"
    fileExtension = u'.json'
    processes = []
    pendingQ = mp.Queue()
    updateQ = mp.Queue()
    waitForResume = mp.Queue()
    
    # the time in seconds before a worker thread is being killed
    timeout = 600.0

    # start errorHandling process    
    ep = mp.Process(target=journalHandler, args=(pendingQ, updateQ, waitForResume, workingDir))
    ep.start()
    
    # block until journalHandler has initialized the 'pending' list
    waitForResume.get()
    
    numFiles = pendingQ.qsize()
    print pendingQ.empty()
    while not pendingQ.empty():
        if len(processes) <= numProcesses:
            filename = pendingQ.get()
            pw = ProcessWorker(filename, workingDir, outputDir, logging, updateQ, fileExtension)
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
                        updateQ.put(('broken', process[2], errString))
                else:
                    processes.remove(process)
        #logging.info(u'{:.2f}% completed'.format((1 - (pendingQ.qsize()/float(numFiles)))*100))
    
    for p in processes:
        p.join()
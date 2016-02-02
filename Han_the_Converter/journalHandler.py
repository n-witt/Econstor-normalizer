import threading
import os
import time
import pickle


class journalHandler(object):
        
    def __init__(self, pendingQ, updateQ, waitForResume, workingDir, logging, dataDir):
        self.logging = logging
        # restricts access to the journal object. this is crucial for pickling
        self.journalLock = threading.Lock()
        pickleFile = dataDir + os.sep + 'journal.pickle'
        # in seconds
        pickleInterval = 30.0
        
        # read pickled journal if exists. create list of files otherwise
        try:
            with open(pickleFile, 'r') as pf:
                with self.journalLock:
                    journal = pickle.load(pf)
                    newFiles = self._updateJournal(journal, workingDir)
                    newFiles = {f: '' for f in newFiles}
                    journal["pending"].update(newFiles) 
        except IOError:
            # create list of all files in `workingDir`
            if os.path.exists(workingDir):
                # journal keeps track of the status of the files ('pending', 'broken', 'complete')
                with self.journalLock:
                    journal = {'pending': {}, 'broken': {}, 'complete': {}}
                docs = os.listdir(workingDir)
                for doc in docs:
                    with self.journalLock:
                        doc = doc.replace('.json','')
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
            self.logging.info("\n\n### STATUS ###\njournal pickled. stats:\ncomplete: {}\nbroken: {}\npending: {}\nsum: {}\ncomplete: {:.2f}%\n".format( \
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
   
    def _updateJournal(self, journal, workingDir):
        '''
        find files that are not contained in the journal and return them
        '''
        docs = os.listdir(workingDir)
        oldList = set()
        for l in journal.itervalues():
            for item in l.keys():
                oldList.add(item + '.json')

        newList = set(docs) - oldList
        return list(newList)
    
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
                    self.logging.error("invalid journal message received")

    def __getItem(self, updateQ):
        while True:
            item = updateQ.get()
            if item == 'terminate':
                break
            yield item

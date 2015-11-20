'''
Created on 19.11.2015

@author: nils witt
'''
import Queue
import threading
import multiprocessing
import os
import pdf2text
import logging

logging.getLogger().setLevel(logging.INFO)
numThreads = multiprocessing.cpu_count()
threadList = []
for i in range(numThreads):
    threadList.append("Thread-" + str(i))
workingDir = "files"    
queueLock = threading.Lock()
threads = []
threadID = 1

class myThread (threading.Thread):
    def __init__(self, name, q, wd):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.wd = wd

    def run(self):
        print("Starting " + self.name)
        process_data(self.q, self.wd)
        print("Exiting " + self.name)

def process_data(q, wd):
        while not q.empty():
            try:
                queueLock.acquire()
                filename = q.get()
                queueLock.release()
                plaintext = pdf2text.convert_pdf_to_txt(wd + os.sep + filename)
                plainFilename = filename + ".txt" 
                if not os.path.exists(wd + os.sep + plainFilename):
                    fd = open(wd + os.sep + plainFilename, "w+")
                    fd.write(plaintext)
                    logging.info(plainFilename + " written")
            except Exception as e:
                logging.info("I/O error({0}): {1}".format(e.errno, e.strerror))
                continue

def fillQueue(path):
    if os.path.exists(path):
        docs = os.listdir(path)
        q = Queue.Queue()
        queueLock.acquire()
        for doc in docs:
            q.put(doc)
        queueLock.release()
        return q
    else:
        raise Exception("path was not a valid path")


if __name__ == "__main__":
    
    q = fillQueue("files")
    # Create new threads
    for tName in threadList:
        thread = myThread(tName, q, workingDir)
        thread.start()
        threads.append(thread)

    # Wait for queue to empty
    #while not q.empty():
    #    pass

    # Wait for all threads to complete
    for t in threads:
        t.join()
    print("Exiting Main Thread")
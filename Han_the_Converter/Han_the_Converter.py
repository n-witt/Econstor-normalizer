import multiprocessing as mp
import os
import logging
from processingPdfFiles.processingPdfFiles import ProcessWorker
from journalHandler import journalHandler
import time

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    numProcesses = mp.cpu_count()
    dataDir = '../data'
    workingDir = dataDir + os.sep + 'pdf'
    outputDir = dataDir + os.sep + 'json'
    fileExtension = u'.json'
    processes = []
    pendingQ = mp.Queue()
    updateQ = mp.Queue()
    waitForResume = mp.Queue()
    
    # the time in seconds before a worker thread is being killed
    timeout = 600.0

    # start errorHandling process    
    jh = mp.Process(target=journalHandler, args=(pendingQ, updateQ, waitForResume, workingDir, logging, dataDir))
    jh.start()
    
    # block until journalHandler has initialized the 'pending' list
    waitForResume.get()
    
    numFiles = pendingQ.qsize()
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
    logging.info('Done')

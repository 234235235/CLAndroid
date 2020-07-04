# Default
import sys
import os
from tqdm import tqdm



# JNI
import JNI.JNI_Finder as JNIF
import JNI.JNI as JNI

# Lib
import LIB.LIB_Finder as LIBF
import LIB.LIB as LIB

# Joern
import Joern.Joern as Joern


# Custom

from Helper.helper import cprint
# Multiprocessing

from multiprocessing import Process
from multiprocessing import JoinableQueue as Queue

#runInfos

maxProcesses = 2
maxThreads = 2    

tag = "[static_analysis_main] "
 
def main(frame_path,libOut,jniOut):
    
    if not os.path.exists(libOut):
        os.makedirs(libOut)
    if not os.path.exists(jniOut):
        os.makedirs(jniOut)
    
    ###################
    ####### JNI #######
    ###################

    ## find JNI ##
    
    #JNIF.detectJNIs(framework_path=jni_test_path,outDir=jniOut)
    #JNIF.detectJNIs(framework_path=jni_test_path,outDir=jniOut) #cprint version 
    
    JNIF.detectJNIs(framework_path=frame_path,outDir=jniOut)
    
    ## OR load JNIs ##

    """   
    cprint(tag+"Loading JNIs..")
    safed_jnis = jniOut
    JNIs = []
    for jni in tqdm(os.listdir(safed_jnis)):
        if (jni.endswith(".xml")):
            JNIs.append(JNI.load(safed_jnis+os.path.sep+jni))
    cprint(tag+"\nDone.\n")
    """
    #cprint(JNIs)
    
    

    ###################
    ###### Libs #######
    ###################

    ## find libs ##

    #LIBF.detectLIBs(framework_path=lib_test_path,outDir=libOut)
    #LIBF.detectLIBs(framework_path=lib_test_path,outDir=libOut) # cprint version
    LIBF.detectLIBs(framework_path=frame_path,outDir=libOut)

    ## OR load LIBs ##

    """
    cprint(tag+"Loading LIBs...\n")
    safed_libs = libOut
    LIBs = []

    for lib in tqdm(os.listdir(safed_libs)):
        if lib.endswith(".xml"):
            LIBs.append(LIB.load(safed_libs+os.path.sep+lib))
    cprint("\n"+tag+"Done.\n")
    """
    
    #find headers (optional)

    
    ########################################
    ###### Joern (CPP2Propertygraph) #######
    ########################################

    #TODO: Edit Joern/Joern.py path variables on top

    #cprint("Creating Property Graphs with Joern Tool...\n")

    #cprint("Running Joern in "+str(maxProcesses)+" processes and "+str(maxThreads)+" threads each.")
    #joern(LIBs)
    
    #cprint("\n\nDone.\n")
   


"""
def joern(LIBs):
    procQueue = Queue()  
    pBar = Queue()
    
    processes = spawnProcesses(maxProcesses,Joern.run,(procQueue,pBar,joernOut,maxThreads,))
 
    for p in processes:
        p.deamon = True
        p.start()     

    LIBs = LIBs[:5]
    
    for lib in LIBs:
        procQueue.put(lib)

    for x in tqdm(range(len(LIBs))):
        while True:
            if not pBar.empty():
                pBar.get()
                break
            
    procQueue.join()  

    # stop subprocesses
    
    for i in range(len(processes)):
        procQueue.put(None)

    for p in processes:
        p.join()


    procQueue.join()
    return
    
"""

def spawnProcesses(nbr,target,args):
    processes=[]
    if __name__ == '__main__':
        processes = []
        for x in range(nbr):
           p = Process(target=target,args=args)
           p.deamon = True
           processes.append(p)
           
        
    

    return processes


    
if __name__ == '__main__':
    if (len(sys.argv) < 4):
        print(tag+"To less arguments...")
        exit(0)
        
    main(sys.argv[1],sys.argv[2],sys.argv[3])

    
    

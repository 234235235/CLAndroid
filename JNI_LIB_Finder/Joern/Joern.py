import subprocess as sp
import os
from tqdm import tqdm
#import queue
from multiprocessing import JoinableQueue as Queue
from multiprocessing import Process
from threading import Thread


# Mingw64
#mingw64 = r"S:\Programme\git\Git\usr\bin\mintty.exe"
#mingw32 = r"S:\Uni\Master\SS18\embsec\Ex4\ChipSoftware\msys32\mingw32.exe"
console = r"S:\Programme\git\Git\git-bash.exe"
joernLocation = "S://Programme/Joern/joern-cli/bin"

tag = "[Joern/Joern.py]"

q = Queue()
#pbar = Queue()


def createPropertyGraph(lib,outDir):    
    joerncmd = "./joern-parse "
    joerncmd += str(lib.getPath())+" "
    name = lib.getName().replace(".cpp",".zip")
    joerncmd += "--out '"+outDir+os.path.sep+name+"'"
    
    cmd = console+" -c "+'"(cd '+joernLocation+" && "+joerncmd+')"'
    
    cmd = cmd.replace("\\","//")
    cmd = cmd.replace("\\\\","//")
    
    #print(cmd)

    #does not work
    """
    si = sp.STARTUPINFO()
    si.dwFlags = sp.STARTF_USESHOWWINDOW
    si.wShowWindow = sp.SW_HIDE
    cflags = sp.CREATE_NO_WINDOW

    with  sp.Popen(cmd,stdout=sp.PIPE,creationflags=sp.CREATE_NO_WINDOW) as proc:#,startupinfo=si,creationflags=cflags) as proc:
        print(proc.stdout.read())
    """        
    shell = sp.Popen(cmd,stdout=sp.PIPE)#,startupinfo=startupInfo)#,creationflags=sp.CREATE_NEW_CONSOLE)
              
    out,err = shell.communicate()



def worker(outDir,pBar):
    #global pbar
    
    while True:
        lib = q.get()
        if lib is None:
            q.task_done()
            break
        
        createPropertyGraph(lib,outDir)
        #pbar.put(True)
        pBar.put(True)
        q.task_done()            

def run(procQueue,pBar,outDir,maxThreads=1):
    
    isNone = False
    while True:
        libs = []
        elements = []
        for i in range(maxThreads):
            try:
                x = procQueue.get(False)
            except:
                break
            elements.append(x)
            if not (x is None):
                libs.append(x)
            else:
                isNone = True
                break
            
        if (len(libs)>0):
            run2(pBar,libs,outDir,maxThreads)

        for i in range(len(elements)):
            #pBar.put(True)
            procQueue.task_done()
            
        if isNone:
            break

        
def run2(pBar,libs,outDir,maxThreads=1):
    #print(str(os.getpid())+": "+"RUNNING-"+str(len(libs)))
   
    #global pbar

    if (len(libs) < maxThreads):
        maxThreads = len(libs)
    
    
    
    threads = []
   
    for i in range(maxThreads):
        t = Thread(target=worker,args=(outDir,pBar,))
        t.deamon = True
        t.start()
        threads.append(t)    
    
    for lib in libs:
        q.put(lib)

    """
    #Progressbar cheat
    for x in tqdm(range(len(libs))):
        while True:
            if not pbar.empty():
                pbar.get()
                break

    """    
    q.join()


    #stop worker
    for i in range(maxThreads):
        q.put(None)

    for t in threads:
        t.join()

    return


def test():
    curr = os.getcwd()
    os.chdir(r"S:\Programme\Joern\joern-cli\bin")
    cd = sp.Popen([gitBash,"-c","(cd S://Desktop && mkdir hi)"],stdin=sp.PIPE,stdout=sp.PIPE,shell=True)
    out,err = cd.communicate()

    print(out)
    print(err)
    os.chdir(curr)






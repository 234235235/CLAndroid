import os
import pathlib
import sys

from tqdm import tqdm
import LIB.LIB as LIB
from Helper.helper import cprint

path = pathlib.Path(__file__).parent.absolute().parent.parent
sys.path.append(str(path))

from Default.Colors import Color

frame_path = ""
tag = Color.ORANGE.value+"[LIB_Finder] "+Color.RESET.value
done = Color.GREEN.value+"DONE!"+Color.RESET.value

def getCPPFiles(path,firstTime=False):
    if (firstTime):             
        files = []
        try:
            for dirOrFile in tqdm(os.listdir(path)):
                try:
                    if os.path.isfile(os.path.join(path,dirOrFile)):
                        if(dirOrFile.endswith(".cpp") or dirOrFile.endswith(".c")):
                            files.append(os.path.join(path,dirOrFile))
                    else:
                        files.extend(getCPPFiles(os.path.join(path,dirOrFile)))
                except Exception as e:
                    cprint(tag+"ERROR#1: "+str(e))
                    cprint(tag+"ERROR#1: "+str(os.path.join(path,dirOrFile)))

        except Exception as e:
            cprint(tag+"ERROR: "+str(e))
            cprint(tag+"ERROR: "+str(path))
        return files    

    
    else:
        files = []
        try:
            for dirOrFile in os.listdir(path):
                try:
                    if os.path.isfile(os.path.join(path,dirOrFile)):
                        if(dirOrFile.endswith(".cpp") or dirOrFile.endswith(".c")):
                            files.append(os.path.join(path,dirOrFile))
                    else:
                        files.extend(getCPPFiles(os.path.join(path,dirOrFile)))
                except Exception as e:
                    cprint(tag+"ERROR#2: "+str(e))
                    cprint(tag+"ERROR#2: "+str(os.path.join(path,dirOrFile)))
        except Exception as e:
            cprint(tag+"ERROR#3: "+str(e))
            cprint(tag+"ERROR#3: "+str(path))

        return files

def genLIB(file):
    try:
        with open(file,"r",errors="ignore") as f:
            for line in f.readlines():
                #edited if ("JNINativeMethod" in line):
                if ("JNIEnv" in line):
                    return LIB.generateLIB(file)
    except Exception as e:
        cprint(tag+"ERROR#4: "+str(file))
        cprint(tag+"ERROR#4: "+str(e))

    return None
    

def detectLIBs(framework_path="",outDir=None):
    frame_path = framework_path

    if not (os.path.isdir(frame_path)):
         raise Exception(tag+"detectLIBs():\n framework_path Directory not found: '"+frame_path+"' !")

    if not (outDir is None):
        if not (os.path.isdir(outDir)):
             raise Exception(tag+"(detectLIBs()):\n outDir Directory not found: '"+outDir+"' !")
    

    #collect possible libs
    cprint(tag+"Collecting possible LIB files...")
    files = getCPPFiles(frame_path,firstTime=True)
    cprint("\n"+tag+"Collecting possible LIB files... "+done)
    
    LIB_Files = []

    cprint(tag+"Detecting Libraries...")
    for file in tqdm(files):
        res = genLIB(file)
        if not (res is None):
            LIB_Files.append(res)

    cprint("\n"+tag+"Detecting Libraries... "+done)
	
  
	
    if (outDir == None):
        for lib in LIB_Files:
            cprint(lib)

    else:
        cprint(tag+"Storing Files...")
        for lib in tqdm(LIB_Files):
            lib.store(outDir)
        cprint("\n"+tag+"Storing Files... "+done)

    cprint(tag+"Total: "+Color.CYAN.value+str(len(LIB_Files))+" LIBs"+Color.RESET.value)

    return LIB_Files
    
    

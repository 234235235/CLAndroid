# -*- coding: cp1252 -*-
import os
import re
import sys
import pathlib

import JNI.JNI as JNI
from tqdm import tqdm
from Helper.helper import cprint


path = pathlib.Path(__file__).parent.absolute().parent.parent
sys.path.append(str(path))

from Default.Colors import Color



frame_path = ""
tag =Color.ORANGE.value+"[JNI_Finder] "+Color.RESET.value
done = Color.GREEN.value+"DONE!"+Color.RESET.value

def configure(framework_path=""):
    frame_path = framework_path

#finds java files which could be the JNI
def getJavaFiles(path,firstTime=False):
        
    if (firstTime):             
        files = []
        for dirOrFile in tqdm(os.listdir(path)):
            if os.path.isfile(path+os.path.sep+dirOrFile):
                if(dirOrFile.endswith(".java")):
                   files.append(path+os.path.sep+dirOrFile)
            else:
                files.extend(getJavaFiles(path+os.path.sep+dirOrFile))

        return files
    
    else:
        files = []
        try:
            for dirOrFile in os.listdir(path):
                if os.path.isfile(path+os.path.sep+dirOrFile):
                    if(dirOrFile.endswith(".java")):
                        files.append(path+os.path.sep+dirOrFile)
                else:
                    files.extend(getJavaFiles(path+os.path.sep+dirOrFile))
        except Exception as e:
            print(tag+"~getJavaFiles~"+Color.ORANGE.value+"Exception occured, but ignoring: "+Color.RESET.value)
            print(tag+"~getJavaFiles~"+Color.ORANGE.value+str(e)+Color.RESET.value)
        return files
            
            
def genJNI(file):

    #checks if file is a JNI, and if so generates the JNI with
    #JNI.generateJNI(file)
    pattern = r'(private|public) (.*)(static)?(.*)native (.*)'
    with open(file,"r",errors='ignore') as f:
        for line in f.readlines():
            result = re.search(pattern,line)
            if not (result is None):
                try:
                    return JNI.generateJNI(file) # can also run on other thread
                except Exception as e:
                    cprint(tag+"genJNI~ Could not generate JNI for file: "+str(file))
                    return None
        return None
           
        #content = f.read() # attention: what about large files what is faster?
        #if 'native' in content: #is this sufficient?
            #return True
        #return False
        

def prettyPrintJNIs(files):
    for file in files:
        spl = file.split(os.path.sep)
        cprint(spl[len(spl)-1])
        
        
#returns list of class JNI (including native methods defined in JNI)
def detectJNIs(framework_path="",outDir=None):
    frame_path = framework_path
    
    if not (os.path.isdir(frame_path)):
        raise Exception(tag+"(detectJNIs()):\n framework_path Directory not found: '"+frame_path+"' !")

    if not (outDir is None):
        if not (os.path.isdir(outDir)):
             raise Exception(tag+"(detectJNIs()):\n outDir Directory not found: '"+outDir+"' !")
            
    #get possible JNI files
    cprint(tag+"Collecting possible JNI files...")
    files = getJavaFiles(frame_path,firstTime=True)
    cprint("\n"+tag+"Collecting possible JNI files... "+done)

    #check if they are JNI files
    #can be multiple trheads later!
    JNI_Files = []

    #test_val = 3
    cprint(tag+"Finding JNI files...")
    for file in tqdm(files):
        #returns none if file is not a JNI
        res = genJNI(file)
        if not (res is None):            
            JNI_Files.append(res)
            #test_val = test_val - 1
           # if (test_val == 0):
               # exit()
       
    
    cprint("\n"+tag+"Finding JNI files... "+Color.GREEN.value+"DONE!"+Color.RESET.value)
    
    if (outDir == None):
        for jni in JNI_Files:
            print(jni)
    else:
        for jni in JNI_Files:
            jni.store(outDir)
        
    cprint(tag+"Total: "+Color.CYAN.value+str(len(JNI_Files))+" JNIs"+Color.RESET.value)
    return JNI_Files


    
              
                        
                        
                




    
    
        
    

from LIB.Function import Method
import re
from Helper.helper import cprint

tag = "[Native_Func_Decl_Detector] "
debug = False

mp = {"jint": "I",
      "jbyte": "B",
      "jshort": "S",
      "jlong":"J",
      "jfloat":"F",
      "jdouble":"D",
      "jchar":"C",
      "jboolean":"Z",
      "jobject":"L",
      }

def translate(string):
    string = string.strip()
    if (string in mp):
        return mp[string]
    """else:
        print("Not supported: ",string)
    """
    return string


def getNativeFunctions(file):
    #print("\n\n#################")
    #print(file)
    #print("------------------")
    ###gather native method declaration(s)
    
    content = ""
    inDeclaration = False
    pattern = "{\s*"

    declarations = []
    bodies = []
    openB = 0
    bc = ""
    inbody = False

    with open(file,"r",errors="ignore") as f:
        if (debug): print("Parsing file",file)

        for l in f.readlines():
            if (debug): print("Current line: ",l)

            if inDeclaration:
                content = content +"\n"+l

            tstl = l.replace(" ", "")
            if (("JNIEXPORT " in tstl) or ("JNICALL" in tstl) or ("(JNIEnv" in tstl) and not inDeclaration):
                content = l
                inDeclaration = True

            if not (re.search(pattern,content) is None):
                #print("MATCHED",content)
                if (inDeclaration == True):
                    inbody = True
                    if (debug): print("INBODY SET TO TRUE")
                inDeclaration = False
                declarations.append(content)
                content = ""


            if inbody:
                if not (l.strip() == ""):
                    if not (openB == 0):
                        bc += l
                    else:
                        bc += "{\n"+l.split("{",1)[1]
                    #print("LINE ADDED",l)

                ob = l.count("{")
                cb = l.count("}")

                openB += ob - cb

            if openB <= 0 and inbody:
                bodies.append(bc)
                bc = ""
                inbody = False
                openB = 0
            ##Simple trick: somitimes they also declare those methods
            ##with help of pointers e.g. JNINAtiveMethod* this results in
            ##a bug if only "JNINAtiveMethod" and not with whitespace
            ##but with whitespace this should be fine.

    if (debug):
        for x in declarations:
            cprint(x)
        cprint("BODIES:")
        for bd in bodies:
            cprint("------------BD--------------------")
            cprint(bd)
            cprint("------------BD END--------------------")
        cprint("BODIES END#########################")

        cprint("LENGHT %i Body, %i Declarations"%(len(bodies),len(declarations)))

    ###split gathered information in functions

    methods = []

    for i in range(len(declarations)):
        content = declarations[i]
        body = bodies[i]
        if (debug):
            print("Current content:\n",content)
            print("According body:\n",body)
        
        try: 
            editedContent = content.split("(",1)[0]
        except BaseException as err:
            cprint(tag+"getNativeFunctions(file) s.th. went wrong during editing content:\n")
            cprint("Content: \n"+content)
            cprint("Error Message:\n"+err)
            continue


        #print("Edited Content:")
        #print(editedContent)

        funcDecl = editedContent.strip()

        name = "NOT_Found"
        try:
            name = editedContent.strip().split(" ")
            name = name[len(name) - 1]
            name = name.split("_")
            name = name[len(name)-1]
        except Exception as e:
            cprint(tag+"ERR#1",e)

        signature="NOT_FOUND"

        ret = "NOT_Found"

        try:
            if ("JNIEXPORT") in funcDecl:
                ret = funcDecl.strip().split(" ")[1]
                ret = translate(ret)
        except Exception as e:
            cprint(tag + "ERR#3", e)

        try:
            signature = content.split("(")[1].split(")")[0]
            s = signature.split(",")[2:]
            signature = []
            for arg in s:
                signature.append(arg.strip().split(" ")[0])

            signature = [translate(sig) for sig in signature]

            signature = "(" + "".join(signature) + ")" + ret
        except Exception as e:
            cprint(tag+"ERR#2",e)




        #print("NAME",name)
        #print("Sig",signature)
        #print("decl",funcDecl)
        method = Method(name=name,signature=signature,func=funcDecl,body=body)
        methods.append(method)
        #print(method)
        #exit()

    #for x in methods:
    #    print(x)
    #print("#################")
    return methods

def test():
    pattern = "{(.*)}(,?)"
    s  = 'static const JNINativeMethod gAnimatedImageDrawableMethods[] = {'
    s += '{"nCreate","(JLandroid/graphics/ImageDecoder;IIJZLandroid/graphics/Rect;)J",'
    s += '(void*) AnimatedImageDrawable_nCreate }'
    print(s)
    res = re.findall(pattern,s,re.DOTALL)
    print(res)
    print("\n\nTADA:")
    [print(x) for x in res]



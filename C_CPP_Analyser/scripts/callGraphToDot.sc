import scala.collection.mutable.ListBuffer
import scala.io.Source

import io.shiftleft.codepropertygraph.generated.nodes.Method

import java.io.{File => JFile}
import java.io.PrintWriter
import java.io.FileWriter
import java.util.regex.Pattern


def getFileLocation(): String = {
	for (x <- cpg.file.name.l){
		if (x != ""){
			return x
		}
	}
	return ""
}				

def createCallGraph(): String = {
	
	var dot = "digraph CallGraph{\n"


	//TODO IGNORE ALL SYSTEM FUNCTIONS!
	var exclude = new ListBuffer[String]();
	
	exclude += "<operator>"
	
	
	var methodNames = new ListBuffer[Method]();
	
	for (method <- cpg.method.l){
		if (!exclude.exists(method.name.contains(_))){
			methodNames.append(method)
		}
	}
	
	/*
	println("GOT METHODS: ")
	for (m <- methodNames){
		println(m.name);
	}*/
	
	
	var f = new JFile(getFileLocation())
	//var fileName = cpg.file.name.head.replace("\\","/")
	var fileName = f.getName()	
	
	for (m <- methodNames){
		
		var methodString = "";
		
		
		var name_escaped = Pattern.quote(m.name)
		
		//println(name_escaped)
		//println(cpg.method.name(name_escaped).l)

		try{
			if (cpg.method.name(name_escaped).head.astParentFullName == "<global>"){
				methodString = "EXT::: "+m.name+"::: "+fileName;
			} else{
				methodString = fileName+"::: "+m.name+"::: "+getFileLocation();
			}
			
			for (caller <- cpg.method.name(name_escaped).caller.l){
				fileName=fileName.replace("\"","\\")
				var callerName=caller.name.replace("\"","\\")
				var location=getFileLocation()
				dot += "\""+fileName+"::: "+callerName+"::: "+location  + "\" -> \"" + methodString.replace("\"","\\") +"\"\n";
			}
			
			if (cpg.method.name(name_escaped).caller.l.length == 0){
				dot += "\""+methodString.replace("\"","\\")+"\"\n"
			}
		} catch {
			case e: Throwable => println("Exception during node creation of method"+m+"\n"+e+"\nIgnoring.")
			
		}
	}
	
	dot += "}"
	return dot
}

def getIncludes(path: String): String = {
	var incl = ""
	
	for (line <- Source.fromFile(path).getLines()){
		if (line.contains("¤#include")){
			incl += line+"\n"
		}
	}
	
	println(incl)
	return incl;
}

def errorOut(outFile: String="None",error: String="None"): Unit = {
	var out = outFile + ".err"
	val wr = new PrintWriter(new JFile(out))
	wr.write(error)
	wr.close()
}				

											   
@main def main(cpgFile: String="None", outFile: String="None",inclOut: String="None"): Unit = {
	//println(inclOut)
	try{
		if (cpgFile!="None"){
			loadCpg(cpgFile);
		}
	
		var dot = createCallGraph();
		//println("DOT:\n"+dot.toString())
		
		if (dot != ""){
			if (outFile != "None"){	
				val writer = new PrintWriter(new JFile(outFile));
				writer.write(dot.toString());
				writer.close();
			}
			
			if (inclOut != "None"){
				var incl = getIncludes(getFileLocation()); //cpg.file.name.head);
				if (incl != ""){
					val w = new PrintWriter(new JFile(inclOut))
					w.write(incl.toString());
					w.close();
				}
			}
		}
	} catch {
		case e: Exception => errorOut(outFile,e.toString());
	}
	
	return 
}

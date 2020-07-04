#!/bin/bash

BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`


#main stuff
mainPath="path_to_folder_where_this_file_is_in"
py=python3 #python version e.g. python.bat or python3 or phyton for windows, needs to be python 3 version
joernPath="...Programme/Joern/" #folder to joern location !Make sure to use the Joern version supplied with 
								#this tool, otherwhise you need to change some commands since its a tool
								#in development.

#Database
db_location="...\Neo4j\neo4j-community-3.5.18\bin" #folder to neo4j installation folder
db_Uri="bolt://localhost:7687"
#db_Uri="bolt://188.210.62.191:7687"
db_User="neo4j"
db_Pword="neo4j"
#IMPORTANT! Also change commands on clean.sh (in same folder) if you run this tool on windows 
#i.e. neo4j -> neo4j.bat and cypher-shell -> cypher-shell.bat
#SAME for Neo4JServer file

#JNI_LIB_Finder

jni_lib_finder="${mainPath}JNI_LIB_Finder/"


test_path="${mainPath}tstFiles/fullTest" #root folder of ur project to analyse

#Output directories

outDir="${mainPath}Out/"


time_log="${outDir}time.log"
c_cpp_out="${outDir}/C_CPP_Analyser/"
out_libs_summary="${outDir}/JNI_LIB_Finder/LIBs/"
out_jni_summary="${outDir}/JNI_LIB_Finder/JNIs/"
vulSummaryCsv="${outDir}C_CPP_Analyser/summary.csv"
vulSummaryResolvedCsv="${outDir}C_CPP_Analyser/summary_resolved.csv"
java_out="${outDir}Java/"
totalSummary="${outDir}summary_complete.csv"
#C / CPP Analysis
#IMPORTANT: Also edit paths on C_CPP_Analyser/main.sh !!!
c_cpp_analyser="${mainPath}C_CPP_Analyser/"


#Java Analysis
java_analyser="${mainPath}Java_Analyser/"

tag="${RED}[MAIN]${RESET} "
done="${GREEN}DONE!${RESET}"
skip="${tag}${RED}SKIPPED!${RESET}"


##arg parse

cleanFst="false"
modus="FULL"

printhelp(){
	echo "### USAGE "
	echo "### ./ultra_main.sh [-c] [-f] [-h]"
	echo "### -c clean/delete out directory (${CYAN}${outDir}${RESET}) before usage" 
	echo "### -f run in fast mode, default: FULL"                                    
	echo "### ##### "
	exit 0
}

#logFile=${outDir}/defaultLog.txt

while getopts "cfh:" option
do
case ${option}
in
c) cleanFst="true";;
f) modus="FAST";;
h) printhelp;;
#l) logFile=$OPTARG
esac
done



echo "${tag}Using python version: ${CYAN}$($py --version)${RESET}"


if [[ $cleanFst == *"y"* || $cleanFst == "true" ]]; then
	echo "${tag}Deleting/Cleaning out dir: ${CYAN}${outDir}${RESET}..."
	rm -r $outDir
	echo "${tag}Deleting/Cleaning out dir: ${CYAN}${outDir}${RESET}... ${done}"
	echo "${tag}Cleaning Neo4j Graph..."
	./clean.sh $mainPath $db_location $db_Uri $db_User $db_Pword
	echo "${tag}Cleaning Neo4j Graph... ${done}"
fi

source GETDIFF


if [[ ! -d "$outDir" ]]; then
	mkdir $outDir
fi

echo "${tag}Collecting JNI & LIB files..."
strt=$(date)
(cd $jni_lib_finder &&
	$py static_analysis_main.py $test_path $out_libs_summary $out_jni_summary) |& tee "${outDir}M_jni_lib_finder.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "JNI_LIB_Finder: $res" >> $time_log
echo "${tag}(${res})Collecting JNI & LIB files... ${done}"
#exit 0

echo "${tag}Starting Database..."
./Neo4JServer $db_location start
#echo $skip
echo "${tag}Starting Database... ${done}"


echo "${tag}Running C/CPP Analysis..."
strt=$(date)
(cd $c_cpp_analyser &&
	./main.sh $c_cpp_analyser $test_path $c_cpp_out $out_libs_summary $out_jni_summary $db_Uri $db_User $db_Pword $mainPath $py $modus $joernPath $time_log)
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "C_C++_Analyser: $res" >> $time_log
#exit 0
echo "${tag}Running C/CPP Analysis... ${done}"
#exit 0

echo "${tag}Linking vulnerable native calls to JNI if possible..."
strt=$(date)
(cd $jni_lib_finder &&
	./link_native_to_jni.sh $jni_lib_finder $vulSummaryCsv $out_libs_summary $out_jni_summary $py) |& tee "${outDir}M_link_native_to_jni.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "JNI_LIB_Linker: $res" >> $time_log
echo "${tag}Linking vulnerable native calls to JNI if possible... ${done}"
#exit 0

#Be sure that ur compiled code (i.e. Jar files) are also reachable from the defined test_path
#Otherwhise change test_path here
#test_path=rootfolder (..../jar_files.jar)

echo "${tag}Running java analyser..."
strt=$(date)
(cd $java_analyser && ./main.sh $vulSummaryResolvedCsv $test_path $java_out $totalSummary $c_cpp_analyser $db_Uri $db_User $db_Pword $mainPath $py $time_log)
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "Java_Analyser: $res" >> $time_log

echo "${tag}Running java analyser... ${done}"
#exit 0

if [[ ! -d "$outDir/log" ]]; then
	mkdir "$outDir/log"
fi

for file in $(find $outDir -name "*.log")
do
	mv $file "$outDir/log"
done

echo "${tag}Stopping Database..."
./Neo4JServer $db_location Stop
#echo $skip
echo "${tag}Stopping Database... ${done}"

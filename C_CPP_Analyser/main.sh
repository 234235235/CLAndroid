#!/bin/bash

directory=$1 #@see ultra_main.sh: mainPath
filePath=$2
outDir=$3 #@see ultra_main.sh: outDir
#filePath=$2 for later!

## EDIT END ##


#These don't have to be edited, just if wanted.

lib_xml=$4
jni_xml=$5
db_Uri=$6
db_User=$7
db_Pword=$8
rootDir=$9
py=${10}
modus=${11}
joernPath=${12}
time_log=${13}


binFilePath="${outDir}cpgs/"
callGraphOutDir="${outDir}dot/"
scriptPath="${directory}scripts/"
joernDir="${joernPath}joern-cli/"
csvFile="${outDir}summary.csv" #if this is edited need to be set to same value
									  #as vulSummaryCsv @see: ultra_main.sh
detailedOutPath="${outDir}detailed/"
#inclOut="${outDir}includes/"
inclOut="${outDir}incl2/"
crossCalls="${outDir}crossCalls/"
detailedVul="${outDir}vul/"

errFile="${outDir}toDB.err"

#dot2pngLoc=".../dot2png.bat"



BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`

tag="${RED}[C/CPP MAIN]${RESET} "
skip="${tag}${RED}SKIPPED!${RESET}"

getDiff(){
	strt=$1
	stp=$2
	
	diff=$(( $(date -d "$stp" "+%s") - $(date -d "$strt" "+%s") ))
	
	diffh=$(date -d@$diff -u +%H:%M:%s)
	
	echo $diffh

}

if [[ ! -d $outDir ]]; then
	echo "${tag}Creating new output folder: ${CYAN}${outDir}${RESET}..."
	mkdir $outDir
	echo "${tag}Creating new output folder: ${CYAN}${outDir}${RESET}... ${GREEN}DONE!${RESET}"
fi

strt=$(date)
#############################         Parse Source Files             #######################################

echo "${tag}Applying Joern on source code..."
echo "${tag}Directory: ${CYAN}${filePath}${RESET}"
./codeImport.sh $joernPath $filePath $binFilePath |& tee "${outDir}C_codeImport.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "C_CPP_Analyser:::codeImport $res" >> $time_log
echo "${tag}${CYAN}(${res})Applying Joern on source code... ${GREEN}DONE!${RESET}"

#############################    END  Parse Source Files     END     #######################################

#############################     search for vulnerabilities         #######################################
strt=$(date)
echo "${tag}Searching for potential vulnerabilities..."
./detectVulnerabilites.sh $binFilePath $joernDir $scriptPath $detailedVul $outDir |& tee "${outDir}C_detectVulnerabilities.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "C_CPP_Analyser:::detectVulnerabilities $res" >> $time_log
echo "${tag}${CYAN}(${res})Searching for potential vulnerabilities... ${GREEN}DONE!${RESET}"
#exit 0
#############################  END search for vulnerabilities  END    ######################################

#############################     generate includes         #######################################
strt=$(date)
echo "${tag}Generating includes with modus ${CYAN}${modus}${RESET}..."
./genInclude.sh $scriptPath $filePath $inclOut $db_Pword $db_User $db_Uri $rootDir $py $outDir $modus |& tee "${outDir}C_includeGenerator.log"
###(cd $scriptPath && $py includeGenerator.py $filePath $inclOut $db_Pword $db_User $db_Uri $rootDir) |& tee "${outDir}C_includeGenerator.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "C_CPP_Analyser:::includeGenerator $res" >> $time_log
#exit 0
echo "${tag}${CYAN}(${res})Generating includes with modus ${CYAN}${modus}${RESET}... ${GREEN}DONE!${RESET}"
#############################  END generate includes   END    ######################################



#############################        create call graph               #######################################
strt=$(date)
echo "${tag}Creating callgraph..."
echo "${tag}Creating local callgraph..."
./callGraphToDot.sh $joernDir $binFilePath $callGraphOutDir $scriptPath $inclOut $modus $outDir |& tee "${outDir}C_callGraphToDot.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "C_CPP_Analyser:::callGraphToDot $res" >> $time_log
#exit 0
echo "${tag}${CYAN}(${res})Creating local callgraph... ${GREEN}DONE!${RESET}"
############################  END   create call graph END          ##########################################


############################          create global graph           #########################################

strt=$(date)
echo "${tag}Linking local callgraphs to global callgraph..."
#(cd $callGraphOutDir && dot2png.bat)
./transferToDatabase.sh $scriptPath $callGraphOutDir $inclOut $db_Uri $db_User $db_Pword $crossCalls $rootDir $py $errFile $filePath $time_log |& tee "${outDir}C_transferToDatabase.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "C_CPP_Analyser:::transferToDatabase $res" >> $time_log
#echo "${tag}${CYAN}(${res})Linking local callgraphs to global callgraph...  ${GREEN}DONE!${RESET}"
echo "${tag}Creating callgraph... ${GREEN}DONE!${RESET}"
#exit 0
#############################   END  create glboal graph      END      #######################################




#############################         Backwards tracking             #######################################
strt=$(date)
echo "${tag}Applying Backwards slicing for potential vuln functions..."
./backwardsSlicing.sh $joernDir $scriptPath $binFilePath $crossCalls $detailedOutPath $csvFile $outDir $outDir |&tee "${outDir}C_backwardsSlicing.log"
#echo $skip
stp=$(date)
res=$(getDiff "$strt" "$stp")
echo "C_CPP_Analyser:::backwardsSlicing $res" >> $time_log
echo "${tag}${CYAN}(${res})Applying Backwards slicing for potential vuln functions... ${GREEN}DONE!${RESET}"



#############################   END   Backwards tracking   END       #######################################

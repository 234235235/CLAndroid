BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`

tag="${BLUE}[backwardsSlicing]${RESET} "

joernDir=$1
scriptPath=$2
binFilePath=$3
crossCalls=$4
detailedOutPath=$5
csvFile=$6
vulPath=$7
logPath=$8/log

if [ ! -d $detailedOutPath ]; then
echo "${tag}Creating new output folder: ${CYAN}${detailedOutPath}${RESET}..."
mkdir $detailedOutPath
echo "${tag}Creating new output folder: ${CYAN}${detailedOutPath}${RESET}... ${GREEN}DONE!${RESET}"
fi

if [[ ! -d $logPath ]]; then
	mkdir $logPath
fi

for f in $vulPath/*.vul
do 

#BUGGY: ASSUMPTION: 1 line free after last entry!

while read LINE; 
do
#fileName=${file/\.bin\.zip/""}
#fileName=${fileName/\.c/""}
#variable=x
#func=func3

#echo "${tag} LINE: ${LINE}"
opts=($(echo $LINE | tr ";" "\n"))

func=${opts[0]}
vulLine=${opts[1]}
location=${opts[2]}


fileName=($(echo $location | tr "/" "\n"))
fileName=${fileName[-1]}
fileName=${fileName/\.cpp/""}
fileName=${fileName/\.c/""}


echo "${tag}Applying backwards slicing for ${CYAN}${func}: ${vulLine} (${location}) ${RESET}..."
#out=$
cpgName=$fileName
same=$(find $binFilePath \( -name "$fileName.bin.zip" -o -name "${fileName}_*.bin.zip" \) )
same=($(echo $same | tr " " "\n"))
#echo ${same[@]} | tr " " "\n"
if [[ ${#same[@]} -gt 1 ]]; then
	for cpg in ${same[@]}
	do
		#echo $cpg
		cntxt=$(cat $cpg | grep $location)
		if [[ $cntxt == *"matches"* ]]; then
			cpgName=($(echo $cpg | tr "/" "\n"))
			cpgName=${cpgName[-1]}
			cpgName=${cpgName/\.bin\.zip/""}
			#echo $cpgName
			break
		fi
	done
fi

(cd $joernDir &&
	./joern --script "${scriptPath}backwardsSlicing.sc" --params "cpgPath=${binFilePath},cpgName=${cpgName},func=${func},lnNbrStr=${vulLine},crossCalls=${crossCalls},outFile=${detailedOutPath}${cpgName}.dot,csvFile=${csvFile}" > "$logPath/$cpgName.out")
#echo $out
echo "${tag}Applying backwards slicing for ${CYAN}${func}: ${vulLine} (${location}) ${RESET}... ${GREEN}DONE!${RESET}"

done < $f

done

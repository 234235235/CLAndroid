#!/bin/bash

source UPDATE

joernPath=$1    
joernServer="${joernPath}joern-server/"
joernCLI="${joernPath}joern-cli/"
joernCpg="${joernPath}cpg/cpgclientlib/"

filePath=$2    
outDir=$3      


BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`
tag="${BLUE}[codeImport]${RESET} "

export _Java_OPTS="-Xmx20G"  #20GB of ram 

#include create update
#source UPDATE


if [ ! -d "$outDir" ]; then
echo "${tag}Creating new output folder: ${CYAN}${outDir}${RESET}..."
mkdir -p $outDir
echo "${tag}Creating new output folder: ${CYAN}${outDir}${RESET}... ${GREEN}DONE!${RESET}"
fi

createCPG(){
	start=$1
	end=$2
	id=$3
	pid=$BASHPID

	curr=0
	
	echo "${tag}[$start-$end]createCPG with pid $CYAN$pid($id)$RESET started!"

	#for file in ${filePath}*.cpp ${filePath}*.c
	for file in  $(find $filePath -maxdepth 10000 \( -name "*.cpp" -o -name "*.c" \))
	do
		skip=$((curr < $start))
		endCond=$((curr >= $end))
		curr=$((curr + 1))
		
		if [[ $skip -eq 1 ]]; then
			continue
		fi

		if [[ $endCond -eq 1 ]]; then
			break
		fi

		fileName=($(echo $file | tr "/" "\n"))
		fileName=${fileName[-1]}
		fileName=${fileName/\.cpp/""}
		fileName=${fileName/\.c/""}

		#echo "${tag}Parsing file ${CYAN}${fileName}${RESET} ..."

		cpgFileName="${outDir}${fileName}.bin.zip"
		i=0
		while [[ -f "$cpgFileName" ]]
		do
			cpgFileName="${outDir}${fileName}_$i.bin.zip"
			i=$((i+1))
			#echo "${tag}Skipping, since already processed. For overwriting run ultra_main.sh with -c"
		done
		
		(cd $joernCLI && ./joern-parse $file --out "${cpgFileName}" > /dev/null 2>&1)

		updateCur $pid $id
		#curr=$((curr+1))
		#echo "${tag}[${curr}/${total}]Parsing file ${CYAN}${fileName}${RESET} ... ${GREEN}DONE!${RESET}"

	done
	
	echo "${tag}[$start-$end]createCPG with pid $CYAN$pid($id)$RESET $GREEN DONE! $RESET"
	
	doneId $id $pid

}



total=$(find $filePath -maxdepth 10000 \( -name "*.cpp" -o -name "*.c" \) | wc -l)
currP=0
id=0

multi=$((total > 100))
batches=1
split=50
maxP=20

if [[ $multi -eq 1 ]]; then
	batches=$((total / $split))
	batches=$((batches + 1))
fi

echo "${tag}Got a total of ${CYAN}$total files${RESET}!"

for batch in $(seq $batches)
do
	start=$(((batch-1) * $split))
	end=$((batch * $split))

	if [[ $currP -eq $maxP ]]; then
		echo "Max processes reached. Waiting."
		wait -n
		currP=$((currP - 1))
	fi

	createCPG $start $end $id &
	currP=$((currP+1))
	id=$((id+1))
done

wait
echo "${tag}All files processed!"







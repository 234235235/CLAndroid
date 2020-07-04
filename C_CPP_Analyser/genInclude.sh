#!/bin/bash

BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`

tag="${BLUE}[genInclude]${RESET} "

scriptPath=$1
srcDir=$2
inclOut=$3
dbP=$4
dbU=$5
dbUri=$6
rootD=$7
py=$8
vulDir=$9
modus=${10}

max=20
cur=0
id=0

total=$(find $srcDir \( -name "*.h" -o -name "*.hpp" -o -name "*.c" -o -name "*.cpp" \) | wc -l)
#total=10

multi=$((total > 1))
batches=1
split=500 #000000

if [[ $multi -eq 1 ]]; then
	batches=$((total / $split))
	batches=$((batches + 1)) 
fi

echo "${tag} Got a total of ${CYAN}$total files${RESET}!"

for batch in $(seq $batches)
do	
	
	start=$(((batch-1)*$split))
	end=$((batch * $split))
	
	if [[ $end -gt $total ]]; then
		end=$total
	fi
			
	if [[ $cur -eq $max ]]; then
		echo "Waiting cuz max processes reached!"
		wait -n
		cur=$((cur - 1))
	fi
	
	(cd $scriptPath && $py includeGenerator.py $srcDir $inclOut $dbP $dbU $dbUri $rootD $start $end LOAD) & 
	
	cur=$((cur + 1))
	id=$((id+1))

done

wait


(cd $scriptPath && $py includeGenerator.py $srcDir $inclOut $dbP $dbU $dbUri $rootD -1 -1 GENINCL $vulDir $modus)  
	

echo "${tag} All files processed!"

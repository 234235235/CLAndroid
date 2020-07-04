BLUE=`tput setaf 4`
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
CYAN=`tput setaf 6`

scriptDir=$1
csvFile=$2
lib_xml=$3
jni_xml=$4
py=$5

tag="${BLUE}[link_native_to_jni]${RESET} "
done="${GREEN}DONE !${RESET}"


echo "${tag}Adding according JNI calls to found vulnerabilites (${CYAN}@see: summary.csv${RESET})..."
echo "${tag}Using: ${CYAN}${lib_xml}${RESET}"
echo "${tag}Using: ${CYAN}${jni_xml}${RESET}"
(cd $scriptDir && $py link_native_to_jni.py $csvFile $lib_xml $jni_xml)
echo "${tag}Adding according JNI calls to found vulnerabilites (${CYAN}@see: summary.csv${RESET})... ${done}"

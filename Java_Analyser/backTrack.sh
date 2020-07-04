#!/bin/bash
javaOut=$1
totalSummary=$2

kind=appJar

#TODO java8=TODO/Jdk8/bin/java.exe
java8=$JAVA_HOME/bin/java

exclusionFile=$(pwd)/exclusions.txt 

while read LINE;
do

args=($(echo $LINE | tr ";" "\n"))

jarFile=${args[0]}
bt=${args[@]:1:${#args[@]}}

echo "${jarFile}"
echo "$bt"

#$java8 -jar bws.jar -$kind $jarFile -out $javaOut -exclusionFile $exclusionFile -bt $bt
$java8 -jar bws_debug.jar -$kind $jarFile -out $javaOut -exclusionFile $exclusionFile -bt "$bt"


done < "${javaOut}/todo.txt"

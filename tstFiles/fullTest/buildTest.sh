#!/bin/bash
#
javaFiles=$(pwd)/java
jarName=exponent.jar
buildDir=$(pwd)/build
nativeDir=$(pwd)/native


dynLibName=dynamic.dll
stLibName=static.dll
dynCppFile=JNI_JNI_Helper_Dynamic.cpp
stCppFile=JNI_JNI_Helper_Static.cpp

vul=vulnerable.cpp
helper=helper.cpp

echo Building jar file...
(cd $javaFiles && find . -maxdepth 100 -type f -name "*.class" -exec rm {} +)


(cd $javaFiles && javac -h . MainClass.java)

(cd $javaFiles && jar cfve $jarName MainClass -C $javaFiles .)

#echo "Testing if jar build successfull: "
#(cd $javaFiles && java -jar $jarName)

mkdir -p $buildDir/Java
mkdir -p $nativeDir/header

mv $javaFiles/$jarName $buildDir/Java/
mv $javaFiles/*.h $nativeDir/header
echo Building jar file... DONE!


echo Building library...
(cd $nativeDir && x86_64-w64-mingw32-g++ -I"${JAVA_HOME}/include" -I"${JAVA_HOME}/include/win32" -shared -o $dynLibName $dynCppFile $vul $helper)
(cd $nativeDir && x86_64-w64-mingw32-g++ -I"${JAVA_HOME}/include" -I"${JAVA_HOME}/include/win32" -shared -o $stLibName $stCppFile)

mkdir -p $buildDir/Libs

(cd $buildDir/Libs && rm *.dll)

mv $nativeDir/*.dll $buildDir/Libs

echo Building library... DONE!


echo Test build done.


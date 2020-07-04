#include <jni.h>
#include <iostream>
#include <cstring>
#include "header/JNI_JNI_Helper_Dynamic.h"
#include "header/helper.h"

using namespace std;

jint JNI_OnLoad(JavaVM *vm, void *reserved){
	cout << "Dynamic.cpp: OnLoad called. But not needed." << endl;
	
	return JNI_VERSION_1_4;
}


JNIEXPORT jint JNICALL Java_JNI_JNI_1Helper_1Dynamic_computeExpo
  (JNIEnv *env, jobject thisObj, jint base, jint expo){
	cout << "Dynamic.cpp: Computing exponent!" << endl;
	return 0;
	  
 }
 
 JNIEXPORT jint JNICALL Java_JNI_JNI_1Helper_1Dynamic_getNumberFor
	(JNIEnv *env, jobject thisObj, jstring toInt){
	const char *inCStr = env->GetStringUTFChars(toInt,NULL);
	
	if (NULL == inCStr) return -1;
	
	cout << "Dynamic.cpp: Translating string to int for: " << inCStr << endl;
	
	//copy
	size_t len = strlen(inCStr);
	char *toint = new char[len+1];
	strncpy(toint,inCStr,len);
	toint[len] = '\0';
	
	
	env->ReleaseStringUTFChars(toInt,inCStr);
		
	int res = safe(toint);
	
	return res;
  }
 


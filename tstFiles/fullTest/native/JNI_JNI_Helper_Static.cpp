#include <jni.h>
#include <iostream>
#include "header/JNI_JNI_Helper_Static.h"

using namespace std;


JNIEXPORT jint JNICALL test(JNIEnv *env, jclass thisObj, jint base, jint expo){
	  cout << "Static.cpp: test aka computeExpoStatic called" << endl;
	  return -1;
}

jint JNI_OnLoad(JavaVM* vm, void* reserved){
	JNIEnv *env;
	cout << "Static.cpp: JNIOnload called!" << endl;
	
	JNINativeMethod methods[] = {
		{	"computeExpoStatic",
			"(II)I",
			(void *) test
		}
	};
	
	vm->GetEnv((void **) &env, JNI_VERSION_1_4);
	
	jclass cls = env->FindClass("JNI/JNI_Helper_Static");
	
	env->RegisterNatives(cls,methods,sizeof(methods)/sizeof(methods[0]));
	
	return JNI_VERSION_1_4;
	
}




JNIEXPORT jint JNICALL Java_JNI_JNI_1Helper_1Static_computeExpoStaticV2
  (JNIEnv *env, jclass thisObj, jint base, jint expo){
	  cout << "Static.cpp: Returning -1" << endl;
	  return -100;
	  
}
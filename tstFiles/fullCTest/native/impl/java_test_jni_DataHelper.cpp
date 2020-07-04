#include <jni.h>
#include <native/header/helper.hpp>

JNIEXPORT jstring JNICALL Java_java_test_jni_DataHelper_ngetData(JNIEnv *env, jobject obj, jint size){
	printf("java_test_jni_DataHelper.cpp TODO");
	return "hiho";
	
}


JNIEXPORT void JNICALL Java_java_test_jni_DataHelper_nstoreData(JNIEnv *env, jobject obj, jstring str){
	//const char *inCStr = (*env)->GetStringUTFChars(env, inJNIStr, NULL);
    //if (NULL == inCStr) return NULL;
	
	safe(str); //todo make right.
	//(*env)->ReleaseStringUTFChars(env, inJNIStr, inCStr);
	
	printf("java_test_jni_DataHelper.cpp: Data saved.");
	return;
}

static const JNINativeMethod gMethods[] = {
	{"nstoreData" , "Ljava/lang/String;)V", (void) Java_java_test_jni_DataHelper_nstoreData }
};



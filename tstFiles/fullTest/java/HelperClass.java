import JNI.JNI_Helper_Static;
import JNI.JNI_Helper_Dynamic;

public class HelperClass{

	public int compute(int nbr, int exponent){
		System.out.println("HelperClass: compute called");
		System.out.println("Using static jni helper...");
		int jniRes = JNI_Helper_Static.exponentiate(nbr,exponent);
		System.out.println("Got res: "+jniRes);
		System.out.println("Using dynamic jni helper...");
		JNI_Helper_Dynamic jhd = new JNI_Helper_Dynamic();
		jniRes = jhd.exponentiate(nbr,exponent);
		System.out.println("Got res: "+jniRes);
		return jniRes;
	}
	
}
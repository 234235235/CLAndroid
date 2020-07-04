package JNI;

public class JNI_Helper_Dynamic{
	static{
		System.loadLibrary("dynamic");
	}
	public int exponentiate(int base, int expo){
			System.out.println("JNI_Dynamic: exponentiate called, forwarding to native code for computation...");
			int cRes = computeExpo(base,expo);
			System.out.println("JNI_Dynamic: got as res of computeExpo("+base+","+expo+": "+cRes);
			String nstring = ""+cRes;
			System.out.println("JNI_Dynamic: converted to string: "+nstring);
			cRes = getNumberFor(nstring);
			System.out.println("JNI_Dynamic: converted via native to int again: "+cRes);
			return cRes;
	}
	
	private native int computeExpo(int base, int expo);
	private native int getNumberFor(String s);
	
}
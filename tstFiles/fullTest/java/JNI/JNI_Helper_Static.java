package JNI;

public class JNI_Helper_Static{
	static{
		try{			
			System.loadLibrary("static");
		} catch (Exception e){
			System.out.println("Failed to load static lib.");
		}
	}

	public static int exponentiate(int base, int expo){
			System.out.println("JNI_Static: exponentiate called, forwarding to native code for computation...");
			int cRes = 100;
			try{
				cRes = computeExpoStatic(base,expo);
				int wtf = computeExpoStaticV2(base,expo);
				System.out.println("JNI_Static: also works without registering, same as dynamic..: "+wtf);
				//cRes = 1000;
			} catch (Exception e){
				System.out.println("failed to use static lib");
			}
			return cRes;
	}
	
	private static native int computeExpoStatic(int base, int expo);
	private static native int computeExpoStaticV2(int base, int expo);
	
}
package java.test.jni;


public final class DataHelper {
	
	private native String ngetData(int bSize);	
	private native void nstoreData(String data);
	
	public void storeData(String data){
		nstoreData(data);		
	}
	
	public String getData(int size){
		String retrieved = ngetData(size);
		
		if (retrieved == null){
			System.err.println("Failure retrieving data! Returning empty string.");
			return "";
		}
	
		return retrieved;
	}
	
	
}
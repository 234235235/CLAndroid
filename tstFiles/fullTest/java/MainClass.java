public class MainClass{
	public static void main(String[] args){
			System.out.println("main of MainClass.java called!");
			HelperClass hc = new HelperClass();
			
			int res = hc.compute(2,5);
			
			System.out.println("Result: "+res);
					
	}
	
}
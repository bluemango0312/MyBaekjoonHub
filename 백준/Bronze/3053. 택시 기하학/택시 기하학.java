import java.io.*;
import java.util.*;

public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int num = Integer.parseInt(br.readLine());
		System.out.println(Math.PI * Math.pow(num, 2));
		System.out.println(2 * Math.pow(num, 2));
	}

}

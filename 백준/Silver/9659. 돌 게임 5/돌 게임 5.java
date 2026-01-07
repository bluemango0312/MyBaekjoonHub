import java.io.*;
import java.util.*;

public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		long N = Long.parseLong(br.readLine());

		if (N % 4 == 0 || N % 4 == 2) {
			System.out.println("CY");
		} else {
			System.out.println("SK");
		}
	}

}

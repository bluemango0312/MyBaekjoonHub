import java.io.*;

public class Main {
	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int n = Integer.parseInt(br.readLine());

		int result = 0;

		if (n % 8 == 0) {
			result = 2;
		} else {
			result = n % 8;
			if (result > 5) {
				result = 10 - result;
			}
		}

		System.out.println(result);
	}
}

import java.io.*;
import java.util.*;

public class Main {
	public static void main(String[] args) throws NumberFormatException, IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int N = Integer.parseInt(br.readLine());
		int M = Integer.parseInt(br.readLine());
		String input = br.readLine();
		String str = "IOI";
		int result = 0;

		// 대상 문자열 만들기
		for (int i = 1; i < N; i++) {
			str += "OI";
		}

		// 비교
		for (int i = 0; i <= input.length() - str.length(); i++) {
			String partStr = "";

			for (int j = 0; j < str.length(); j++) {
				partStr += input.charAt(i + j);
			}

			if (partStr.equals(str)) {
				result++;
			}
		}

		System.out.println(result);
	}

}

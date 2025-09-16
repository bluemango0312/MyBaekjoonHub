import java.io.*;
import java.util.*;

public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int N = Integer.parseInt(br.readLine());
		StringBuilder sb = new StringBuilder();

		while (N != -1) {
			// 약수 찾기
			List<Integer> divisors = new ArrayList<>();

			for (int i = 1; i < N; i++) {
				if (N % i == 0) {
					divisors.add(i);
				}
			}

			// 해당 약수들을 다 더해서 N이 되는지 확인
			int sum = 0;
			for (int i : divisors) {
				sum += i;
			}
			
			if (sum == N) {
				sb.append(N).append(" = ");

				for (int i = 0; i < divisors.size(); i++) {
					sb.append(divisors.get(i));

					if (i != divisors.size() - 1) {
						sb.append(" + ");
					}
				}

				sb.append("\n");
			} else {
				sb.append(N).append(" is NOT perfect.").append("\n");
			}

			N = Integer.parseInt(br.readLine());
		}

		System.out.println(sb);
	}

}

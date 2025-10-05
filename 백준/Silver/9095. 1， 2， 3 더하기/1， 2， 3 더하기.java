import java.io.*;
import java.util.*;

public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int T = Integer.parseInt(br.readLine());
		StringBuilder sb = new StringBuilder();

		for (int tc = 0; tc < T; tc++) {
			int num = Integer.parseInt(br.readLine());

			if (num == 1) {
				sb.append(1).append("\n");
				continue;
			} else if (num == 2) {
				sb.append(2).append("\n");
				continue;
			} else if (num == 3) {
				sb.append(4).append("\n");
				continue;
			}

			int[] dp = new int[num + 1];
			dp[1] = 1;
			dp[2] = 2;
			dp[3] = 4;

			for (int i = 4; i <= num; i++) {
				dp[i] = dp[i - 1] + dp[i - 2] + dp[i - 3];
			}

			sb.append(dp[num]).append("\n");
		}

		System.out.println(sb);
	}

}

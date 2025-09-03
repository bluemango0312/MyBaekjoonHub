import java.io.*;
import java.util.*;

public class Main {
	public static void main(String[] args) throws NumberFormatException, IOException {
		Deque<Integer> dq = new LinkedList<>();
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		StringTokenizer st = new StringTokenizer(br.readLine());

		int N = Integer.parseInt(st.nextToken());
		int K = Integer.parseInt(st.nextToken());
		StringBuilder sb = new StringBuilder();

		sb.append("<");

		for (int i = 0; i < N; i++) {
			dq.add(i + 1);
		}

		while (!dq.isEmpty()) {
			for (int i = 0; i < K - 1; i++) {
				dq.addLast(dq.removeFirst());
			}

			sb.append(dq.getFirst());

			if (dq.size() == 1) {
				break;
			}

			sb.append(", ");

			dq.removeFirst();

		}

		sb.append(">");
		System.out.println(sb);
	}

}

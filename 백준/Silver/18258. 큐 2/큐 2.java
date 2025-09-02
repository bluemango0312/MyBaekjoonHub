import java.io.*;
import java.util.*;

public class Main {
	public static void main(String[] args) throws NumberFormatException, IOException {
		Deque<Integer> dq = new ArrayDeque<>();

		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		int N = Integer.parseInt(br.readLine());
		StringBuilder sb = new StringBuilder();

		for (int i = 0; i < N; i++) {
			StringTokenizer st = new StringTokenizer(br.readLine());
			String cmd = st.nextToken();

			switch (cmd) {
			case "push":
				int num = Integer.parseInt(st.nextToken());
				dq.addLast(num);
				break;

			case "pop":
				if (dq.size() == 0) {
					sb.append("-1").append("\n");
				} else {
					sb.append(dq.removeFirst()).append("\n");
				}
				break;
			case "size":
				sb.append(dq.size()).append("\n");
				break;
			case "empty":
				if (dq.isEmpty()) {
					sb.append("1");
				} else {
					sb.append("0");
				}
				sb.append("\n");
				break;
			case "front":
				if (dq.isEmpty()) {
					sb.append("-1");
				} else {
					sb.append(dq.peekFirst());
				}
				sb.append("\n");
				break;
			case "back":
				if (dq.isEmpty()) {
					sb.append("-1");
				} else {
					sb.append(dq.peekLast());
				}
				sb.append("\n");
				break;
			}
		}
		
		System.out.println(sb);
	}

}

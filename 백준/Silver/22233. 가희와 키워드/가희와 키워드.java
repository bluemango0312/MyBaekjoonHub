import java.io.*;
import java.util.*;

public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		StringTokenizer st = new StringTokenizer(br.readLine());
		int N = Integer.parseInt(st.nextToken()); // 키워드 개수
		int M = Integer.parseInt(st.nextToken()); // 글 수
		Set<String> keywords = new HashSet<>();

		for (int i = 0; i < N; i++) {
			keywords.add(br.readLine());
		}

		for (int i = 0; i < M; i++) {
			String str = br.readLine();
			String[] post = str.split(",");

			for (int j = 0; j < post.length; j++) {
				if (keywords.contains(post[j])) {
					keywords.remove(post[j]);
				}
			}

			System.out.println(keywords.size());
		}

	}

}

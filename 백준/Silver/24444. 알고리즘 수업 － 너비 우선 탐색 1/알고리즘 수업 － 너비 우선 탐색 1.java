import java.io.*;
import java.util.*;

public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		StringTokenizer st = new StringTokenizer(br.readLine());
		int N = Integer.parseInt(st.nextToken()); // 정점의 수
		int M = Integer.parseInt(st.nextToken()); // 간선의 수
		int R = Integer.parseInt(st.nextToken()); // 시작 정점
		List<Integer>[] list = new ArrayList[N + 1];

		// 배열 내부 리스트 초기화
		for (int i = 0; i <= N; i++) {
			list[i] = new ArrayList<>();
		}

		// 무방향 그래프 입력
		for (int i = 0; i < M; i++) {
			st = new StringTokenizer(br.readLine());
			int a = Integer.parseInt(st.nextToken());
			int b = Integer.parseInt(st.nextToken());

			list[a].add(b);
			list[b].add(a);
		}

		// 리스트 내부 오름차순 정렬
		for (int i = 0; i <= N; i++) {
			Collections.sort(list[i]);
		}

		// BFS - queue
		int[] visited = new int[N + 1];

		int turn = 1;
		visited[R] = turn++; // 첫 번째로 방문

		Queue<Integer> queue = new LinkedList<>();
		queue.add(R);

		while (!queue.isEmpty()) {
			int cur = queue.poll();

			for (int n : list[cur]) {
				if (visited[n] == 0) {
					visited[n] = turn++;
					queue.add(n);
				}
			}
		}

		// 결과 출력
		StringBuilder sb = new StringBuilder();
		for (int n = 1; n <= N; n++) {
			sb.append(visited[n]).append("\n");
		}
		System.out.println(sb);
	}

}

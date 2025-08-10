import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Main {
	static int[] visited;
	static int N;
	static int M;

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);

		N = sc.nextInt();
		M = sc.nextInt();

		visited = new int[N + 1];
		List<Integer> result = new ArrayList<>();

		dfs(0, result);
	}

	private static void dfs(int depth, List<Integer> result) {
		if (depth == M) {
			for (int i = 0; i < M; i++) {
				System.out.print(result.get(i));

				if (i != M - 1) {
					System.out.print(" ");
				}
			}
			System.out.println();
		}

		for (int i = 1; i <= N; i++) {
			if (visited[i] == 1)
				continue;

			if (!result.isEmpty() && result.get(result.size() - 1) >= i)
				continue;

			visited[i] = 1;
			result.add(i);

			dfs(depth + 1, result);

			visited[i] = 0;
			result.remove(result.size() - 1);
		}
	}

}

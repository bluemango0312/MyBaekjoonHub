import java.util.Scanner;

public class Main {
	static int cnt = 1;
	static int result = 0;

	public static void main(String[] args) {
		Scanner sc = new Scanner(System.in);
		int N = sc.nextInt();

		if (N == 0) {
			result = 0;
		}else {
			fibo(N, 1, 0);
		}

		System.out.println(result);
	}

	private static void fibo(int n, int current, int prev) {
		if (cnt == n) {
			result = current;
			return;
		}

		cnt++;
		fibo(n, current + prev, current);
	}
}
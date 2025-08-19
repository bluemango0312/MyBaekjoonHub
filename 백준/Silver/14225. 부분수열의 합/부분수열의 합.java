import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        int N = Integer.parseInt(br.readLine());

        // 안전한 입력 파싱: 토큰을 N개 채울 때까지 읽기
        int[] a = new int[N];
        int filled = 0;
        StringTokenizer st = null;
        while (filled < N) {
            if (st == null || !st.hasMoreTokens()) st = new StringTokenizer(br.readLine());
            while (st.hasMoreTokens() && filled < N) {
                a[filled++] = Integer.parseInt(st.nextToken());
            }
        }

        int maxSum = 0;
        for (int x : a) maxSum += x;

        boolean[] can = new boolean[maxSum + 2]; // 1..maxSum+1 체크용
        can[0] = true; // 공집합 합=0 (자연수 탐색엔 영향X)

        // 부분집합 합 표기
        for (int x : a) {
            for (int s = maxSum; s >= 0; s--) {
                if (can[s]) can[s + x] = true;
            }
        }

        // 1부터 첫 false가 답
        for (int t = 1; t <= maxSum + 1; t++) {
            if (!can[t]) {
                System.out.println(t);
                return;
            }
        }
    }
}

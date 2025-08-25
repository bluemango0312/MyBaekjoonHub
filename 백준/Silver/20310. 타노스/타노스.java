// 0과 1로 이루어진 문자열 S
// 0의 개수 & 1의 개수 모두 짝수
// 0 절반, 1 절반 제거
// 가능한 문자열 중 사전순으로 가장 빠른 것

import java.io.*;
import java.util.*;

public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		char[] S = br.readLine().toCharArray();

		// 0이 앞에 오도록 오름차순 정렬
		Arrays.sort(S);

		StringBuilder sb = new StringBuilder();

		// 0과 1 절반 삭제 후 저장
		for (int i = 0; i < S.length; i += 2) {
			sb.append(S[i]);
		}
		
		System.out.println(sb);
	}
}

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));

		Set<String> words = new HashSet<>(); // 중복 자동 방지를 위해 set 사용
		int wordCnt = Integer.parseInt(br.readLine());

		for (int i = 0; i < wordCnt; i++) {
			words.add(br.readLine());
		}

		// sort를 위해 list로 변환
		List<String> wordList = new ArrayList<>(words);
		wordList.sort((e1, e2) -> {
			if (e1.length() != e2.length()) {
				return e1.length() - e2.length(); // 1. 길이 짧은 순
			}

			return e1.compareTo(e2); // 2. 사전 순
		});

		for (String s : wordList) {
			System.out.println(s);
		}
	}

}
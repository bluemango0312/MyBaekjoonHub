import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Scanner;

// 1. 자주 나오는 단어일수록 앞에 배치
// 2. 단어 길이가 길수록 앞에 배치
// 3. 알파벳 사전 순으로 앞에 배치
// M 이상인 단어만 외움

public class Main {
	public static void main(String[] args) throws IOException {
		BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
		
		String[] input = br.readLine().split(" ");
		int wordCnt = Integer.parseInt(input[0]);
		int limitLength = Integer.parseInt(input[1]);
		
		List<String> words = new ArrayList<>();

		for (int i = 0; i < wordCnt; i++) {
			String word = br.readLine();

			if (word.length() >= limitLength) {
				words.add(word);
			}
		}

		// 1. 단어의 빈도수 세서 Map에 저장
		Map<String, Integer> sameWordCnt = new HashMap<>();
		for (String s : words) {
			if (sameWordCnt.containsKey(s))
				sameWordCnt.put(s, sameWordCnt.get(s) + 1);
			else
				sameWordCnt.put(s, 1);
		}

		List<Map.Entry<String, Integer>> entryList = new ArrayList<>(sameWordCnt.entrySet());

		// 2. 정렬
		entryList.sort((e1, e2) -> {
			if (!e1.getValue().equals(e2.getValue())) {
				return e2.getValue() - e1.getValue(); // 빈도수 내림차순
			}
			if (e1.getKey().length() != e2.getKey().length()) {
				return e2.getKey().length() - e1.getKey().length(); // 길이 내림차순
			}
			return e1.getKey().compareTo(e2.getKey()); // 사전 순 오름차순
		});

		// 3. 출력
		StringBuilder sb = new StringBuilder();
	    for (Map.Entry<String, Integer> entry : entryList) {
	        sb.append(entry.getKey()).append('\n');
	    }

	    System.out.print(sb);
	}

}

# Robogram 성취도평가 개발 및 유지보수 규칙 (AGENTS.md)

이 규칙은 Robogram 성취도평가 플랫폼의 Firebase DB 연동 및 채점 시스템 설계 시 반드시 준수해야 하는 규칙 모음입니다. 다른 과목(스마트 팩토리, 자율주행 등)의 분석 대시보드를 추가하거나 수정할 때도 이 아키텍처 원칙을 필히 적용하여 연산 오류를 방지해야 합니다.

---

## 1. 정오답 채점 및 오프셋(Offset) 매칭 원칙
* **학생 제출 답안 형식**: 학생들이 웹에서 문제 풀이 시 제출하는 `responses` 데이터는 **0-based 인덱스 (`0, 1, 2, 3`)**로 DB에 기록됩니다.
* **DB 문항 정답 형식**: 1일차 기초소양 문항은 **1-based 인덱스 (`1, 2, 3, 4`)**를 사용하고, 융합과목(로보미 아바타 등)은 문항 등록 및 파싱 기법에 따라 **0-based 인덱스 (`0, 1, 2, 3`)**가 사용되어 두 포맷이 혼용되어 저장되어 있습니다.
* **비교 매칭 규칙**: 단순히 `studentAns === q.answer`로 비교하면 자료형 및 인덱스 미스매칭 버그가 발생하므로, 반드시 아래의 **양방향 호환 검증 공식**을 사용하여 정오답을 채점하고 보기에 마킹해야 합니다:
  ```javascript
  const isMatch = (String(studentAns) === String(q.answer)) || 
                  (String(Number(studentAns) + 1) === String(q.answer)) ||
                  (String(studentAns) === String(Number(q.answer) + 1));
  ```
* **인적 가독 표기 보정**: 대시보드 하단 회색 정보 상자 등 사용자 화면에 "정답 번호" 및 "작성 답안 번호"를 숫자로 표시할 때는, 컴퓨터용 0-based(`0, 1, 2, 3`) 수치를 그대로 뿌리지 말고 반드시 판단 후 **1을 더한 1-based (`1, 2, 3, 4`)** 정수로 보정하여 출력해야 합니다.

---

## 2. 학적 정보(학년, 반, 번호)의 안전 비교 원칙
* Firebase `answers` 컬렉션의 학적 정보와 `students` 컬렉션의 학적 정보를 비교하여 학생의 응시율 및 성적을 조회할 때, `===` 단순 연산자를 쓰면 숫자(2)와 문자열("2")의 형 불일치로 인해 2일차/3일차 답변이 누락되는 치명적인 버그가 발생합니다.
* 따라서 학년(`grade`), 반(`class`/`classNum`), 번호(`number`)를 필터링할 때는 **무조건 String화 및 공백을 제거한 안전 비교**를 수행해야 합니다:
  ```javascript
  const sAnswers = answers.filter(a => 
    String(a.grade).trim() === String(s.grade).trim() && 
    String(a.classNum).trim() === String(s.class).trim() && 
    String(a.number).trim() === String(s.number).trim()
  );
  ```

---

## 3. 정밀 산술 평균 연산 원칙
* 대시보드 전체 평균 점수 및 학생 리스트 평균 점수를 계산할 때, 전체 데이터 문항 수(`scoringQCount`)의 왜곡 현상을 원천 방지하기 위해 **"각 일차별 100점 만점 환산 점수들의 산술 평균"** 기법을 단일 표준으로 차용합니다.
* 1일차 점수 + 2일차 점수 + 3일차 점수 + ... 를 더한 뒤 전체 일수(`days`)로 나누어 평균값을 구하며, 미응시 일차는 0점으로 계산하여 합산합니다:
  ```javascript
  const calculatedScore = Math.round(dayScores.reduce((sum, val) => sum + val, 0) / days);
  ```
* 이 산술 평균은 렌더링 시점에 실시간 직통 연산으로 꽂아 넣어, 로컬 세션 데이터 캐싱 꼬임 등으로 인한 수치 불일치 가능성을 완벽하게 배제합니다.

# -*- coding: utf-8 -*-
import re
import json

def parse_jam_s_questions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. 정답지 및 해설 영역 파싱
    cards = re.findall(r'<div class="answer-card">(.+?)(?=<div class="answer-card">|</div>\s*<h4|</div>\s*</div>\s*<footer>|\Z)', content, re.DOTALL)
    answer_map = {}
    
    for card in cards:
        q_num_match = re.search(r'Q(\d+)\.', card)
        if not q_num_match:
            q_num_match = re.search(r'Q(\d+)', card)
        if not q_num_match:
            continue
        q_num = int(q_num_match.group(1))
        
        # HTML 엔터티나 공백 제거 후 타겟 찾기
        ans_text_match = re.search(r'<div class="answer-card-ans">\s*(.+?)\s*</div>', card, re.DOTALL)
        if ans_text_match:
            ans_str = ans_text_match.group(1).strip()
            # print(f"Q{q_num} raw: {repr(ans_str)}")
            # 예: "정답: 1) 모델 (Models)" -> "1"
            # 1) 또는 ① 또는 O 또는 1
            num_match = re.search(r'(\d+)\)', ans_str)
            if num_match:
                ans_val = int(num_match.group(1)) - 1
            else:
                if '1)' in ans_str or '①' in ans_str or 'O' in ans_str or '1' in ans_str:
                    ans_val = 0
                elif '2)' in ans_str or '②' in ans_str or 'X' in ans_str or '2' in ans_str:
                    ans_val = 1
                elif '3)' in ans_str or '③' in ans_str or '3' in ans_str:
                    ans_val = 2
                elif '4)' in ans_str or '④' in ans_str or '4' in ans_str:
                    ans_val = 3
                else:
                    ans_val = 0
            answer_map[q_num] = ans_val

    print(f"파싱된 정답 개수: {len(answer_map)}개")

    # 2. 단원별 분할하여 질문 블록 파싱
    parts = re.split(r'<div class="example-section"', content)
    questions_list = []
    
    for part in parts[1:]:
        ex_num_match = re.search(r'id="ex-(\d+)"', part)
        if not ex_num_match:
            continue
        ex_num = int(ex_num_match.group(1))
        
        # 예제 N -> Day (N + 1)
        day_val = ex_num + 1

        # question-card 내부 내용 스캔
        blocks = re.findall(r'<div class="question-card">(.+?)(?=<div class="question-card">|<div class="example-section"|🔑|</body>|\Z)', part, re.DOTALL)
        
        q_order = 1
        for block in blocks:
            q_text_match = re.search(r'<h3 class="q-title">Q(\d+)\.\s*(.+?)</h3>', block, re.DOTALL)
            if not q_text_match:
                continue
            q_num = int(q_text_match.group(1))
            q_content = q_text_match.group(2).strip()
            
            # choices-list 에서 <li> 보기 추출
            raw_opts = re.findall(r'<li class="choice-item">\s*(\d+)\)\s*(.+?)</li>', block)
            if not raw_opts:
                raw_opts = re.findall(r'<li class="choice-item">(.+?)</li>', block, re.DOTALL)
                choices = [re.sub(r'^\d+\)\s*', '', opt).strip() for opt in raw_opts]
            else:
                choices = [opt[1].strip() for opt in raw_opts]

            ans_idx = answer_map.get(q_num, 0)
            
            questions_list.append({
                "item_id": f"JAM-S-Q{q_num:03d}",
                "day": day_val,
                "order": q_order,
                "type": "객관식",
                "content": q_content,
                "choices": choices,
                "answer": ans_idx
            })
            q_order += 1

    print(f"최종 파싱된 잼S 문항 수: {len(questions_list)}개")
    return questions_list

if __name__ == "__main__":
    html_file = r"E:\AI 개발 협업\robogram 성취도평가\roboeval\잼S\예제11편\잼S_성취도평가_110문제.html"
    questions = parse_jam_s_questions(html_file)
    
    output_path = r"E:\AI 개발 협업\robogram 성취도평가\roboeval\잼S\questions_parsed.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print("저장 완료!")

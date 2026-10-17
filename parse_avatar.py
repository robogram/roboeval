# -*- coding: utf-8 -*-
import re
import json

def parse_html_questions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 단원 매칭용 정규식
    chapters = re.findall(r'<h2>(\d+)\s+(.+?)</h2>', content)
    print(f"발견된 단원 수: {len(chapters)}개")

    # 정답지 파싱
    tr_matches = re.findall(r'<tr>\s*<td><b>(\d+)\s*(.+?)</b></td>\s*<td>(.+?)</td>', content, re.DOTALL)
    answer_map = {}
    
    for num_str, title, ans_text in tr_matches:
        # <b>1.</b> ② | **2.** ③ 형태로 파싱 진행
        ans_items = re.findall(r'(?:<b>|\*\*|\b)?(\d+)\.?(?:</b>|\*\*)?\s*([①②③④⑤O X]+)', ans_text)
        for q_num, q_ans in ans_items:
            ans_val = 0
            if '①' in q_ans or 'O' in q_ans:
                ans_val = 0
            elif '②' in q_ans or 'X' in q_ans:
                ans_val = 1
            elif '③' in q_ans:
                ans_val = 2
            elif '④' in q_ans:
                ans_val = 3
            elif '⑤' in q_ans:
                ans_val = 4
            answer_map[int(q_num)] = ans_val

    print(f"파싱된 정답 개수: {len(answer_map)}개")

    # 단원별로 분할하여 질문 블록 파싱
    parts = re.split(r'<h2>', content)
    questions_list = []
    
    for part in parts[1:]:
        chapter_match = re.match(r'(\d+)\s+(.+?)</h2>', part)
        if not chapter_match:
            continue
        chap_num = chapter_match.group(1)
        
        day_map = {
            "02": 2,
            "04": 3,
            "05": 4,
            "06": 5,
            "07": 6,
            "08": 7,
            "09": 8
        }
        day_val = day_map.get(chap_num, 2)

        # 4지선다 파싱을 위해 정규식 보완
        # question-block 내부 내용 전체를 스캔
        blocks = re.findall(r'<div class="question-block">(.+?)(?=<div class="question-block">|<h3>|<h2|🔑|</body>)', part, re.DOTALL)
        
        q_order = 1
        for block in blocks:
            q_text_match = re.search(r'<div class="question">(\d+)\.\s*(.+?)</div>', block, re.DOTALL)
            if not q_text_match:
                continue
            q_num = int(q_text_match.group(1))
            q_content = q_text_match.group(2).strip()
            
            # 보기 추출 (①, ②, ③, ④ 등을 관대하게 긁음)
            options = re.findall(r'<div class="option">([①②③④⑤O X]+)\s*(.+?)</div>', block)
            choices = []
            q_type = "객관식"
            
            if any('O' in opt[0] or 'X' in opt[0] for opt in options):
                q_type = "OX"
                choices = ["O", "X"]
            else:
                # 4지선다 보기를 정확하게 다 긁어오도록 fallback 제거 및 보강
                raw_opts = re.findall(r'<div class="option">(.+?)</div>', block, re.DOTALL)
                choices = [re.sub(r'^[①②③④⑤]\s*', '', opt).strip() for opt in raw_opts]

            ans_idx = answer_map.get(q_num, 0)
            
            questions_list.append({
                "item_id": f"ROBOME-AVATAR-Q{q_num:02d}",
                "day": day_val,
                "order": q_order,
                "type": q_type,
                "content": q_content,
                "choices": choices,
                "answer": ans_idx
            })
            q_order += 1

    print(f"최종 파싱된 문항 수: {len(questions_list)}개")
    return questions_list

if __name__ == "__main__":
    html_file = r"E:\AI 개발 협업\robogram 성취도평가\roboeval\로보미 아바타\gemini-code-1780005702548.html"
    questions = parse_html_questions(html_file)
    
    output_path = r"E:\AI 개발 협업\robogram 성취도평가\roboeval\로보미 아바타\questions_parsed.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print("저장 완료!")

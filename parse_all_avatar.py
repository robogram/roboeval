# -*- coding: utf-8 -*-
import pypdf
import os
import io
import sys
import json

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

def parse_pdf_questions(file_path, start_q_idx, day_val):
    print(f"=== 파싱 진행: {os.path.basename(file_path)} (Day {day_val}) ===")
    reader = pypdf.PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
        
    questions = []
    
    # 1. 🔑 정답지 파싱
    # 정답지는 대략 Q1 ② or Q1 ① 이런 식으로 되어 있음
    answer_map = {}
    ans_matches = re.findall(r'Q(\d+)\s*([①②③④⑤O X]+|[\d]\s*페이지|정답\s*교재)', text)
    # 다른 방식으로 2차 시도
    lines = text.split("\n")
    for line in lines:
        match = re.search(r'Q(\d+)\s*([①②③④⑤]+)', line)
        if match:
            q_num = int(match.group(1))
            q_ans = match.group(2)
            ans_val = 0
            if '①' in q_ans: ans_val = 0
            elif '②' in q_ans: ans_val = 1
            elif '③' in q_ans: ans_val = 2
            elif '④' in q_ans: ans_val = 3
            elif '⑤' in q_ans: ans_val = 4
            answer_map[q_num] = ans_val

    # 만약 정답이 없거나 부족하면 수동 오버라이드 맵 (PDF 내부 정답 확인 결과물과 비교 매칭)
    # 기초블록학습: Q1 ~ Q10
    # 카메라제어: Q1 ~ Q10 (단, 개별 PDF 안의 질문 번호가 Q1~Q10으로 매핑되어 있음)
    # 자신이 그린 가면씌우기: Q1 ~ Q10
    
    # 수동 정답 하드코딩 매칭 (PDF 텍스트 대조 및 오차 방지)
    if "기초블록학습" in file_path:
        # Q1: ②, Q2: ③, Q3: ②, Q4: ②, Q5: ②, Q6: ②, Q7: ②, Q8: ②, Q9: ①, Q10: ②
        pdf_answers = {1: 1, 2: 2, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 0, 10: 1}
    elif "카메라" in file_path:
        # 카메라제어 PDF 정답 확인
        # Q1: ②, Q2: ①, Q3: ②, Q4: ②, Q5: ②, Q6: ②, Q7: ②, Q8: ③, Q9: ②, Q10: ②
        pdf_answers = {1: 1, 2: 0, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 2, 9: 1, 10: 1}
    else: # 자신이 그린 가면씌우기
        # Q1: ③, Q2: ①, Q3: ②, Q4: ④, Q5: ③, Q6: ①, Q7: ②, Q8: ③, Q9: ③, Q10: ①
        pdf_answers = {1: 2, 2: 0, 3: 1, 4: 3, 5: 2, 6: 0, 7: 1, 8: 2, 9: 2, 10: 0}

    # 질문 블록 파싱 [Q1] ... ① ... ② ... ③ ... ④
    # 정규식으로 질문 영역들을 매칭
    q_blocks = re.findall(r'\[Q(\d+)\]\s*(.+?)(?=\[Q\d+\]|🔑|🟨|🟥|🟫|🟩|\Z)', text, re.DOTALL)
    
    order = 1
    for q_num_str, q_body in q_blocks:
        q_num = int(q_num_str)
        
        # 보기 추출 (①, ②, ③, ④)
        # 긴 텍스트에서 보기를 떼어냅니다.
        # 예: ① 바탕화면 ② ...
        lines_body = q_body.split("\n")
        content_lines = []
        option_line = ""
        for line in lines_body:
            if any(opt in line for opt in ['①', '②', '③', '④']):
                option_line += " " + line
            else:
                content_lines.append(line)
                
        content = " ".join(content_lines).strip()
        
        # 정밀 보기 4개 분할 추출
        options = re.findall(r'([①②③④⑤])\s*(.+?)(?=[①②③④⑤]|\Z)', option_line)
        choices = [opt[1].strip() for opt in options]
        
        # 보기가 온전히 파싱되지 않았을 때의 Fallback
        if len(choices) < 4:
            # 텍스트 전체에서 다시 매칭 시도
            options = re.findall(r'([①②③④⑤])\s*(.+?)(?=[①②③④⑤]|\Z)', q_body, re.DOTALL)
            choices = [opt[1].strip() for opt in options]
            
        # 질문 내용에서 보기 텍스트 제거
        for c in choices:
            content = content.replace(c, "")
        content = re.sub(r'[①②③④⑤]\s*', '', content).strip()
        
        # 단원별로 item_id의 유니크 식별 코드 지정
        subject_code = "BLOCK" if "기초블록" in file_path else "CAM" if "카메라" in file_path else "DRAW-MASK"
        
        questions.append({
            "item_id": f"ROBOME-AVATAR-{subject_code}-Q{q_num:02d}",
            "day": day_val,
            "order": order,
            "type": "객관식",
            "content": content,
            "choices": choices[:4], # 최대 4개 보장
            "answer": pdf_answers.get(q_num, 0)
        })
        order += 1
        
    print(f"파싱 완료: {len(questions)}문항 추출됨")
    return questions

import re

if __name__ == "__main__":
    folder = r"E:\AI 개발 협업\robogram 성취도평가\roboeval\로보미 아바타"
    
    # 각 추가 단원들을 파싱하여 적절한 일차(차시)에 매핑합니다.
    # 1. 기초블록학습 ➡ 1일차 (수업 1일차에는 기초블록)
    # 2. 카메라 제어 ➡ 2일차 (기존 2일차였던 얼굴인식 기초와 함께 출제되도록 동일 2일차 매핑)
    # 3. 자신이 그린 가면씌우기 ➡ 8일차 (기존 8일차였던 가면씌우기 뒷부분에 배치)
    
    q_blocks_1 = parse_pdf_questions(os.path.join(folder, "기초블록학습.pdf"), 71, 1)
    q_blocks_2 = parse_pdf_questions(os.path.join(folder, "카메라 제어.pdf"), 81, 2)
    q_blocks_3 = parse_pdf_questions(os.path.join(folder, "자신이 그린 가면씌우기.pdf"), 91, 8)
    
    # 기존 파싱해 두었던 70문항 로드
    parsed_json_path = os.path.join(folder, "questions_parsed.json")
    with open(parsed_json_path, "r", encoding="utf-8") as f:
        existing_questions = json.load(f)
        
    # 신규 30문항 합산
    total_questions = existing_questions + q_blocks_1 + q_blocks_2 + q_blocks_3
    
    # JSON 파일 업데이트
    with open(parsed_json_path, "w", encoding="utf-8") as f:
        json.dump(total_questions, f, ensure_ascii=False, indent=2)
        
    print(f"총 {len(total_questions)}문항으로 통합 업데이트 완료! 🎉")

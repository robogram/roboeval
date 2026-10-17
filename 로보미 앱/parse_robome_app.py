# -*- coding: utf-8 -*-
import pandas as pd
import json
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

# 파일 경로 (로보미 앱 폴더 기준)
current_dir = os.path.dirname(os.path.abspath(__file__))
xlsx_path = os.path.join(current_dir, "로보미앱_1권_2권_수업성취도평가문제집.xlsx")

def clean_answer(ans_val):
    # 정답 값(예: "4번", 4, " 3 번")을 0-based index(0, 1, 2, 3)로 변환
    if pd.isna(ans_val):
        return 0
    ans_str = str(ans_val).strip()
    for char in ans_str:
        if char.isdigit():
            val = int(char)
            if 1 <= val <= 4:
                return val - 1
    return 0

def parse_robome_app_questions():
    if not os.path.exists(xlsx_path):
        print(f"오류: 엑셀 파일이 없습니다. 경로: {xlsx_path}")
        return

    # 1권 문제/답안 로드
    df_q1 = pd.read_excel(xlsx_path, sheet_name='1권_문제')
    df_a1 = pd.read_excel(xlsx_path, sheet_name='1권_답안')
    
    # 2권 문제/답안 로드
    df_q2 = pd.read_excel(xlsx_path, sheet_name='2권_문제')
    df_a2 = pd.read_excel(xlsx_path, sheet_name='2권_답안')
    
    # 조인
    df1 = pd.merge(df_q1, df_a1[['문항ID', '정답', '해설']], on='문항ID', how='inner')
    df2 = pd.merge(df_q2, df_a2[['문항ID', '정답', '해설']], on='문항ID', how='inner')
    
    print(f"1권 로드 완료: {len(df1)} 문항")
    print(f"2권 로드 완료: {len(df2)} 문항")
    
    questions = []
    
    # 1권 처리 (day: 1 ~ 9)
    for idx, row in df1.iterrows():
        chap_num = int(row['단원번호'])
        day_val = chap_num
        
        choices = [
            str(row['①']).strip(),
            str(row['②']).strip(),
            str(row['③']).strip(),
            str(row['④']).strip()
        ]
        
        ans_idx = clean_answer(row['정답'])
        
        questions.append({
            "item_id": f"ROBOME-APP-{row['문항ID']}",
            "day": day_val,
            "order": int(row['단원내번호']),
            "type": "객관식",
            "content": str(row['문제']).strip(),
            "choices": choices,
            "answer": ans_idx
        })
        
    # 2권 처리 (day: 10 ~ 22)
    for idx, row in df2.iterrows():
        chap_num = int(row['단원번호'])
        day_val = chap_num + 9  # 1권 9단원 이후로 이어짐
        
        choices = [
            str(row['①']).strip(),
            str(row['②']).strip(),
            str(row['③']).strip(),
            str(row['④']).strip()
        ]
        
        ans_idx = clean_answer(row['정답'])
        
        questions.append({
            "item_id": f"ROBOME-APP-{row['문항ID']}",
            "day": day_val,
            "order": int(row['단원내번호']),
            "type": "객관식",
            "content": str(row['문제']).strip(),
            "choices": choices,
            "answer": ans_idx
        })
        
    print(f"총 문항 수: {len(questions)}개")
    
    # JSON 저장
    output_json_path = os.path.join(current_dir, "questions_parsed.json")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"파싱 완료 및 JSON 저장 성공: {output_json_path}")

if __name__ == "__main__":
    parse_robome_app_questions()

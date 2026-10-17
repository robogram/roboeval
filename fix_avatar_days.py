# -*- coding: utf-8 -*-
import json
import os

def check_structure():
    json_path = r"E:\AI 개발 협업\robogram 성취도평가\roboeval\로보미 아바타\questions_parsed.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    print("=== 디버깅 및 정밀 매핑 현황 ===")
    print(f"전체 문항수: {len(data)}")
    
    # 각 문항의 ID와 매핑된 일차(day) 확인
    # 우리가 원하는 10차시 표준 융합 단원 매칭
    # 01 기초블록 ➡ 1일차
    # 02 얼굴인식기초 ➡ 2일차
    # 03 카메라제어 ➡ 3일차
    # 04 좌표수치확인 ➡ 4일차
    # 05 표정인식 ➡ 5일차
    # 06 얼굴에화풍적용 ➡ 6일차
    # 07 마스크확인 ➡ 7일차
    # 08 얼굴바꾸기 ➡ 8일차
    # 09 가면씌우기 ➡ 9일차
    # 10 자신이그린가면씌우기 ➡ 10일차

    # 기존 파싱에서 모든 1~70번 문항이 day: 2로 되어 있어 3~7차시가 0개가 되었던 원인을 파악했습니다.
    # 기존 HTML의 <h2> 단원 태그 순서대로 day를 재배치합니다.
    
    for q in data:
        q_id = q.get("item_id", "")
        # 정규식을 이용해 숫자를 발라내거나 ID 규칙에 따라 매칭
        # ROBOME-AVATAR-Q01 ~ Q10 (얼굴인식기초): day 2
        # ROBOME-AVATAR-Q11 ~ Q20 (좌표수치확인): day 4
        # ROBOME-AVATAR-Q21 ~ Q30 (표정인식): day 5
        # ROBOME-AVATAR-Q31 ~ Q40 (화풍적용): day 6
        # ROBOME-AVATAR-Q41 ~ Q50 (마스크확인): day 7
        # ROBOME-AVATAR-Q51 ~ Q60 (얼굴바꾸기): day 8
        # ROBOME-AVATAR-Q61 ~ Q70 (가면씌우기): day 9
        
        if q_id.startswith("ROBOME-AVATAR-Q"):
            try:
                num = int(q_id.replace("ROBOME-AVATAR-Q", ""))
                if 1 <= num <= 10:
                    q["day"] = 2
                elif 11 <= num <= 20:
                    q["day"] = 4
                elif 21 <= num <= 30:
                    q["day"] = 5
                elif 31 <= num <= 40:
                    q["day"] = 6
                elif 41 <= num <= 50:
                    q["day"] = 7
                elif 51 <= num <= 60:
                    q["day"] = 8
                elif 61 <= num <= 70:
                    q["day"] = 9
            except Exception as e:
                pass
        
        # 신규 PDF 단원 매칭 점검
        # ROBOME-AVATAR-BLOCK-Q01 ~ Q50 (기초블록): day 1 (1차시)
        # ROBOME-AVATAR-CAM-Q01 ~ Q10 (카메라제어): day 3 (3차시) - 3차시 문제가 없던 원인 수정!!
        # ROBOME-AVATAR-DRAW-MASK-Q01 ~ Q10 (자신이 그린 가면): day 10 (10차시)
        elif "BLOCK" in q_id:
            q["day"] = 1
        elif "CAM" in q_id:
            q["day"] = 3
        elif "DRAW-MASK" in q_id:
            q["day"] = 10

    # 갱신 데이터 저장
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print("일차별 정밀 매핑 재분포:")
    print({d: len([q for q in data if q['day'] == d]) for d in range(1, 11)})

if __name__ == "__main__":
    check_structure()

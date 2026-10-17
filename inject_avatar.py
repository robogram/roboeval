# -*- coding: utf-8 -*-
import json
import re

def inject_fusion_questions():
    # 1. 파싱된 융합과목 문제집 로드
    json_path = r"E:\AI 개발 협업\robogram 성취도평가\roboeval\로보미 아바타\questions_parsed.json"
    with open(json_path, "r", encoding="utf-8") as f:
        fusion_questions = json.load(f)

    # 2. index.html 파일 로드
    html_path = r"E:\AI 개발 협업\robogram 성취도평가\roboeval\index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 3. index.html에 MASTER_FUSION_QUESTIONS 상수가 있는지 확인 및 주입
    # 이미 상수가 선언되어 있다면 교체, 없으면 MASTER_SOYANG_QUESTIONS 위에 선언
    fusion_js_str = "const MASTER_FUSION_QUESTIONS = " + json.dumps(fusion_questions, ensure_ascii=False, indent=2) + ";\n"

    if "const MASTER_FUSION_QUESTIONS =" in html_content:
        # 기존 상수 영역 교체
        html_content = re.sub(
            r'const MASTER_FUSION_QUESTIONS = \[.*?\];',
            fusion_js_str.strip(),
            html_content,
            flags=re.DOTALL
        )
        print("기존 MASTER_FUSION_QUESTIONS 상수를 성공적으로 교체했습니다!")
    else:
        # MASTER_SOYANG_QUESTIONS 선언 바로 위에 주입
        insertion_target = "const MASTER_SOYANG_QUESTIONS = ["
        if insertion_target in html_content:
            html_content = html_content.replace(
                insertion_target,
                fusion_js_str + "\n" + insertion_target
            )
            print("MASTER_FUSION_QUESTIONS 상수를 새로 성공적으로 주입했습니다!")
        else:
            print("오류: MASTER_SOYANG_QUESTIONS 상수를 찾을 수 없습니다.")
            return

    # 4. index.html 쓰기
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("index.html 업데이트 완료!")

if __name__ == "__main__":
    inject_fusion_questions()

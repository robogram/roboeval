# -*- coding: utf-8 -*-
import json
import re
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(current_dir, "questions_parsed.json")
html_path = os.path.join(current_dir, "..", "index.html")

def inject_app_questions():
    if not os.path.exists(json_path):
        print(f"오류: JSON 파일이 없습니다. 경로: {json_path}")
        return

    # 1. 파싱된 로보미 앱 문제집 로드
    with open(json_path, "r", encoding="utf-8") as f:
        app_questions = json.load(f)

    # 2. index.html 파일 로드
    if not os.path.exists(html_path):
        print(f"오류: index.html 파일이 없습니다. 경로: {html_path}")
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 3. index.html에 MASTER_ROBOME_APP_QUESTIONS 상수가 있는지 확인 및 주입
    app_js_str = "const MASTER_ROBOME_APP_QUESTIONS = " + json.dumps(app_questions, ensure_ascii=False, indent=2) + ";\n"

    if "const MASTER_ROBOME_APP_QUESTIONS =" in html_content:
        # 기존 상수 영역 교체
        # 비그리디 매칭(.*?)을 활용하여 기존 대괄호 상수를 치환
        html_content = re.sub(
            r'const MASTER_ROBOME_APP_QUESTIONS = \[.*?\];',
            app_js_str.strip(),
            html_content,
            flags=re.DOTALL
        )
        print("기존 MASTER_ROBOME_APP_QUESTIONS 상수를 성공적으로 교체했습니다!")
    else:
        # MASTER_FUSION_QUESTIONS 선언 바로 위에 주입
        insertion_target = "const MASTER_FUSION_QUESTIONS = ["
        if insertion_target in html_content:
            html_content = html_content.replace(
                insertion_target,
                app_js_str + "\n" + insertion_target
            )
            print("MASTER_ROBOME_APP_QUESTIONS 상수를 새로 성공적으로 주입했습니다!")
        else:
            # 만약 MASTER_FUSION_QUESTIONS를 못찾는다면 MASTER_SOYANG_QUESTIONS 위에 주입
            insertion_target2 = "const MASTER_SOYANG_QUESTIONS = ["
            if insertion_target2 in html_content:
                html_content = html_content.replace(
                    insertion_target2,
                    app_js_str + "\n" + insertion_target2
                )
                print("MASTER_ROBOME_APP_QUESTIONS 상수를 새로 성공적으로 주입했습니다!")
            else:
                print("오류: 주입 타겟 상수를 찾을 수 없습니다.")
                return

    # 4. index.html 쓰기
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("index.html 업데이트 완료!")

if __name__ == "__main__":
    inject_app_questions()

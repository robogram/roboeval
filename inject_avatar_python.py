import json
import re
import os

def inject_questions():
    json_path = r"e:\AI 개발 협업\robogram 성취도평가\roboeval\로보미 아바타\avatar_python_questions.json"
    if not os.path.exists(json_path):
        print("Parsed JSON file not found!")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        python_questions = json.load(f)

    html_path = r"e:\AI 개발 협업\robogram 성취도평가\roboeval\index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # JS string representations
    python_js_str = "const MASTER_AVATAR_PYTHON_QUESTIONS = " + json.dumps(python_questions, ensure_ascii=False, indent=2) + ";\n"
    pattern_js_str = "const MASTER_AVATAR_PATTERN_QUESTIONS = [];\n" # empty skeleton for now

    if "const MASTER_AVATAR_PYTHON_QUESTIONS =" in html_content:
        # Replace existing
        start_marker = "const MASTER_AVATAR_PYTHON_QUESTIONS = ["
        end_marker = "const MASTER_AVATAR_PATTERN_QUESTIONS = ["
        start_idx = html_content.find(start_marker)
        end_idx = html_content.find(end_marker)
        if start_idx != -1 and end_idx != -1:
            html_content = html_content[:start_idx] + python_js_str + html_content[end_idx:]
            print("Updated MASTER_AVATAR_PYTHON_QUESTIONS successfully!")
        else:
            print("오류: index.html 내에서 선언 영역 매핑에 실패했습니다.")
            return
    else:
        # Inject above MASTER_FUSION_QUESTIONS
        target = "const MASTER_FUSION_QUESTIONS = ["
        if target in html_content:
            html_content = html_content.replace(
                target,
                python_js_str + "\n" + pattern_js_str + "\n" + target
            )
            print("Injected MASTER_AVATAR_PYTHON_QUESTIONS and MASTER_AVATAR_PATTERN_QUESTIONS successfully!")
        else:
            print("Error: Could not find MASTER_FUSION_QUESTIONS inside index.html")
            return

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("index.html updated successfully!")

if __name__ == "__main__":
    inject_questions()

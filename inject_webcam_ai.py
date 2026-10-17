# -*- coding: utf-8 -*-
import json
import re
import os
import sys
import io
import shutil

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

def inject_webcam_ai():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. questions_parsed.json 경로 탐색
    possible_json_paths = [
        os.path.join(current_dir, "웹캠 인공지능", "questions_parsed.json"),
        os.path.join(current_dir, "questions_parsed.json"),
        r"E:\AI 개발 협업\robogram 성취도평가\roboeval\웹캠 인공지능\questions_parsed.json"
    ]
    json_path = None
    for p in possible_json_paths:
        if os.path.exists(p):
            json_path = p
            break

    if not json_path:
        print("오류: questions_parsed.json 파일을 찾을 수 없습니다. parse_webcam_ai.py를 먼저 실행하세요.")
        return False

    with open(json_path, "r", encoding="utf-8") as f:
        webcam_questions = json.load(f)
    print(f"로드된 웹캠 AI 문항 수: {len(webcam_questions)}개")

    # 2. index.html 파일 경로 탐색
    html_path = os.path.join(current_dir, "index.html")
    if not os.path.exists(html_path):
        print("오류: index.html 파일을 찾을 수 없습니다.")
        return False

    # 백업 파일 생성 (index.html.bak 없으면 최초 백업)
    bak_path = html_path + ".bak"
    if not os.path.exists(bak_path):
        shutil.copyfile(html_path, bak_path)
        print(f"최초 원본 백업 완료: {bak_path}")

    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 3. MASTER_WEBCAM_AI_QUESTIONS 상수 주입
    js_const_str = "const MASTER_WEBCAM_AI_QUESTIONS = " + json.dumps(webcam_questions, ensure_ascii=False, indent=2) + ";\n"

    if "const MASTER_WEBCAM_AI_QUESTIONS =" in content:
        content = re.sub(
            r'const MASTER_WEBCAM_AI_QUESTIONS = \[.*?\];\n?',
            js_const_str,
            content,
            flags=re.DOTALL
        )
        print("기존 MASTER_WEBCAM_AI_QUESTIONS 상수를 갱신했습니다.")
    else:
        target_marker = "const MASTER_ROBOME_IOT_QUESTIONS = ["
        if target_marker in content:
            content = content.replace(target_marker, js_const_str + "\n" + target_marker)
            print("MASTER_WEBCAM_AI_QUESTIONS 상수를 새로 주입했습니다 (MASTER_ROBOME_IOT_QUESTIONS 위).")
        else:
            target_fallback = "const MASTER_ROBOME_APP_QUESTIONS = ["
            if target_fallback in content:
                content = content.replace(target_fallback, js_const_str + "\n" + target_fallback)
                print("MASTER_WEBCAM_AI_QUESTIONS 상수를 새로 주입했습니다 (MASTER_ROBOME_APP_QUESTIONS 위).")
            else:
                print("오류: 상수를 주입할 기준 위치를 찾을 수 없습니다.")
                return False

    # 4. <datalist id="subject-list"> 에 옵션 추가
    option_tag = '<option value="웹캠으로 배우는 인공지능">📷 웹캠으로 배우는 인공지능</option>'
    if option_tag not in content:
        pattern_opt = '<option value="로보미 아바타(고등 패턴 파이썬)">🤖 로보미 아바타(고등 패턴 파이썬)</option>'
        if pattern_opt in content:
            content = content.replace(pattern_opt, pattern_opt + "\n                " + option_tag)
            print("과목 datalist에 '웹캠으로 배우는 인공지능' 옵션을 추가했습니다.")
        elif '<datalist id="subject-list">' in content:
            content = content.replace('<datalist id="subject-list">', '<datalist id="subject-list">\n                ' + option_tag)
            print("과목 datalist 최상단에 '웹캠으로 배우는 인공지능' 옵션을 추가했습니다.")

    # 5. renderDayScheduleInputs 내부 webcamAiChapters 정의 및 targetChaptersList 분기 추가
    chapters_code = '''  const webcamAiChapters = [
    { "val": 1, "label": "01. 얼굴인식" },
    { "val": 2, "label": "02. 사물인식" },
    { "val": 3, "label": "03. AI 페르소나" },
    { "val": 4, "label": "04. 캡스톤 통합" },
    { "val": 5, "label": "05. 생성형 AI" }
  ];
'''
    if "const webcamAiChapters =" not in content:
        marker_jams = "  const jamsChapters = ["
        if marker_jams in content:
            content = content.replace(marker_jams, chapters_code + "\n" + marker_jams)
            print("renderDayScheduleInputs 내부에 webcamAiChapters 단원 배열을 추가했습니다.")

    if 'subject.includes("웹캠")' not in content:
        old_target = 'const targetChaptersList = (subject && subject.includes("잼S")) ? jamsChapters :'
        new_target = 'const targetChaptersList = (subject && subject.includes("웹캠")) ? webcamAiChapters :\n                             ((subject && subject.includes("잼S")) ? jamsChapters :'
        if old_target in content:
            content = content.replace(old_target, new_target)
            print("targetChaptersList에 웹캠 과목 분기를 추가했습니다.")

    # 6. 문항 풀 매칭 로직 5곳에 웹캠 분기 추가
    branch_pt1 = '''  if ((cls.subject && cls.subject.includes("웹캠")) && typeof MASTER_WEBCAM_AI_QUESTIONS !== "undefined") {
    fusionPool = MASTER_WEBCAM_AI_QUESTIONS.filter(q => targetChapters.includes(q.day));
  } else if ((cls.subject && cls.subject.includes("로보미 아바타(중등 파이썬)"))'''
    
    branch_pt3 = '''    if ((subject && subject.includes("웹캠")) && typeof MASTER_WEBCAM_AI_QUESTIONS !== "undefined") {
      fusionPool = MASTER_WEBCAM_AI_QUESTIONS.filter(q => targetChapters.includes(q.day));
    } else if ((subject && subject.includes("로보미 아바타(중등 파이썬)"))'''

    branch_pt4 = '''    if ((cls.subject && cls.subject.includes("웹캠")) && typeof MASTER_WEBCAM_AI_QUESTIONS !== "undefined") {
      fusionPool = MASTER_WEBCAM_AI_QUESTIONS.filter(q => targetChapters.includes(q.day));
    } else if ((cls.subject && cls.subject.includes("로보미 아바타(중등 파이썬)"))'''

    branch_pt5 = '''    if ((cls.subject && cls.subject.includes("웹캠")) && typeof MASTER_WEBCAM_AI_QUESTIONS !== "undefined") {
      fusionPool = MASTER_WEBCAM_AI_QUESTIONS.filter(q => targetChapters.includes(q.day));
    } else if ((cls.subject && cls.subject.includes("로보미 아바타(중등 파이썬)"))'''

    branch_pt6 = '''    if ((cls.subject && cls.subject.includes("웹캠")) && typeof MASTER_WEBCAM_AI_QUESTIONS !== "undefined") {
      fusionPool = MASTER_WEBCAM_AI_QUESTIONS.filter(q => q.day === nextDay);
    } else if ((cls.subject && cls.subject.includes("로보미 아바타(중등 파이썬)"))'''

    target_sub = 'if ((subject && subject.includes("로보미 아바타(중등 파이썬)"))'
    if target_sub in content and '((subject && subject.includes("웹캠")) && typeof MASTER_WEBCAM_AI_QUESTIONS' not in content:
        content = content.replace(target_sub, branch_pt3.strip())
        print("지점 3 (반 생성 자동 문제 배정)에 웹캠 풀 분기를 주입했습니다.")

    old_pt1 = '''  if ((cls.subject && cls.subject.includes("로보미 아바타(중등 파이썬)")) && typeof MASTER_AVATAR_PYTHON_QUESTIONS !== "undefined") {
    fusionPool = MASTER_AVATAR_PYTHON_QUESTIONS.filter(q => targetChapters.includes(q.day));'''
    if old_pt1 in content:
        content = content.replace(old_pt1, branch_pt1 + ''' && typeof MASTER_AVATAR_PYTHON_QUESTIONS !== "undefined") {
    fusionPool = MASTER_AVATAR_PYTHON_QUESTIONS.filter(q => targetChapters.includes(q.day));''', 1)
        print("지점 1 (미리보기 문제 풀)에 웹캠 분기를 주입했습니다.")

    old_pt4 = '''    if ((cls.subject && cls.subject.includes("로보미 아바타(중등 파이썬)")) && typeof MASTER_AVATAR_PYTHON_QUESTIONS !== "undefined") {
      fusionPool = MASTER_AVATAR_PYTHON_QUESTIONS.filter(q => targetChapters.includes(q.day));'''
    if old_pt4 in content:
        content = content.replace(old_pt4, branch_pt4 + ''' && typeof MASTER_AVATAR_PYTHON_QUESTIONS !== "undefined") {
      fusionPool = MASTER_AVATAR_PYTHON_QUESTIONS.filter(q => targetChapters.includes(q.day));''', 1)
        print("지점 4 (시험 생성 문제 풀)에 웹캠 분기를 주입했습니다.")

    if old_pt4 in content:
        content = content.replace(old_pt4, branch_pt5 + ''' && typeof MASTER_AVATAR_PYTHON_QUESTIONS !== "undefined") {
      fusionPool = MASTER_AVATAR_PYTHON_QUESTIONS.filter(q => targetChapters.includes(q.day));''', 1)
        print("지점 5 (응시 화면 문제 풀)에 웹캠 분기를 주입했습니다.")

    old_pt6 = '''    if ((cls.subject && cls.subject.includes("로보미 아바타(중등 파이썬)")) && typeof MASTER_AVATAR_PYTHON_QUESTIONS !== "undefined") {
      fusionPool = MASTER_AVATAR_PYTHON_QUESTIONS.filter(q => q.day === nextDay);'''
    if old_pt6 in content:
        content = content.replace(old_pt6, branch_pt6 + ''' && typeof MASTER_AVATAR_PYTHON_QUESTIONS !== "undefined") {
      fusionPool = MASTER_AVATAR_PYTHON_QUESTIONS.filter(q => q.day === nextDay);''', 1)
        print("지점 6 (다음 일차 문제 풀)에 웹캠 분기를 주입했습니다.")

    # 7. 변경사항 저장
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"index.html 업데이트 완료: {html_path}")
    return True

if __name__ == "__main__":
    inject_webcam_ai()

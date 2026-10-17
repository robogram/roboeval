# -*- coding: utf-8 -*-
import pypdf
import os
import io
import sys

# Windows cp949 인코딩 에러 방지용 설정
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

def check_pdf_content(file_path):
    print(f"=== {os.path.basename(file_path)} ===")
    reader = pypdf.PdfReader(file_path)
    text = ""
    for i, page in enumerate(reader.pages):
        text += page.extract_text() or ""
    
    print(f"글자 수: {len(text)}")
    print("--- 처음 1500글자 ---")
    print(text[:1500])
    print("--- 끝 1500글자 ---")
    print(text[-1500:])
    print("\n")

if __name__ == "__main__":
    folder = r"E:\AI 개발 협업\robogram 성취도평가\roboeval\로보미 아바타"
    files = ["기초블록학습.pdf", "카메라 제어.pdf", "자신이 그린 가면씌우기.pdf"]
    for f in files:
        check_pdf_content(os.path.join(folder, f))

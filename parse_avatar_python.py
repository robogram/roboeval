import openpyxl
import json
import os

def parse_excel_questions():
    file_path = r"e:\AI 개발 협업\robogram 성취도평가\roboeval\로보미 아바타\중학생용_파이썬_단원별_4지선다_문제집.xlsx"
    if not os.path.exists(file_path):
        print("Excel file not found!")
        return

    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb.active # '문제 전체'

    rows = list(sheet.iter_rows(values_only=True))
    header = rows[0]

    # Find columns
    idx_total_num = header.index('전체 번호')
    idx_day = header.index('단원')
    idx_day_name = header.index('단원명')
    idx_order = header.index('단원 번호')
    idx_content = header.index('문제')
    idx_opt1 = header.index('①')
    idx_opt2 = header.index('②')
    idx_opt3 = header.index('③')
    idx_opt4 = header.index('④')
    idx_ans_num = header.index('정답 번호')
    
    questions = []
    
    for r in rows[1:]:
        # Skip empty rows or rows without a day value
        if r[idx_day] is None or r[idx_content] is None:
            continue
        
        try:
            day_val = int(r[idx_day])
            order_val = int(r[idx_order]) if r[idx_order] is not None else 1
            total_num = int(r[idx_total_num]) if r[idx_total_num] is not None else len(questions) + 1
        except (ValueError, TypeError):
            continue

        content = str(r[idx_content]).strip()
        choices = [
            str(r[idx_opt1]).strip() if r[idx_opt1] is not None else "",
            str(r[idx_opt2]).strip() if r[idx_opt2] is not None else "",
            str(r[idx_opt3]).strip() if r[idx_opt3] is not None else "",
            str(r[idx_opt4]).strip() if r[idx_opt4] is not None else ""
        ]
        
        # Clean choices if any are empty but keep the array shape
        choices = [c for c in choices if c != ""]
        
        # Determine the answer index (0-based)
        ans_num_str = str(r[idx_ans_num]).strip()
        try:
            # 1-based index in Excel, convert to 0-based
            ans_val = int(float(ans_num_str)) - 1
        except (ValueError, TypeError):
            ans_val = 0 # Fallback
            print(f"Warning: Invalid answer number '{ans_num_str}' at row with total_num {total_num}. Fallback to 0.")

        questions.append({
            "item_id": f"ROBOME-AVATAR-PY-Q{total_num:03d}",
            "day": day_val,
            "order": order_val,
            "type": "객관식",
            "content": content,
            "choices": choices,
            "answer": ans_val
        })

    print(f"Successfully parsed {len(questions)} questions.")
    
    output_path = r"e:\AI 개발 협업\robogram 성취도평가\roboeval\로보미 아바타\avatar_python_questions.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    parse_excel_questions()

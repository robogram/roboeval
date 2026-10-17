import csv
import json
import os

csv_path = r"e:\AI 개발 협업\robogram 성취도평가\roboeval\robogram_lms_180_items_master_v2.csv"
output_dir = r"C:\Users\User\.gemini\antigravity\scratch"
output_path = os.path.join(output_dir, "master_questions.js")

questions = []

with open(csv_path, mode='r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if not row.get('item_id'):
            continue
        
        try:
            pool_no = int(row['pool_no'])
        except Exception:
            pool_no = row['pool_no']
            
        try:
            item_num = int(row['item_num'])
        except Exception:
            item_num = row['item_num']
            
        try:
            answer = int(row['answer_no']) - 1
        except Exception:
            answer = 0
            
        choices = [
            row.get('opt1', ''),
            row.get('opt2', ''),
            row.get('opt3', ''),
            row.get('opt4', '')
        ]
        
        questions.append({
            'item_id': row['item_id'],
            'grade': row['grade'],
            'pool_no': pool_no,
            'item_num': item_num,
            'domain': row['domain'],
            'question': row['question'],
            'choices': choices,
            'answer': answer
        })

os.makedirs(output_dir, exist_ok=True)

# Format the JavaScript file content
js_content = f"const MASTER_SOYANG_QUESTIONS = {json.dumps(questions, ensure_ascii=False, indent=2)};\n"

with open(output_path, mode='w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Successfully converted {len(questions)} items to {output_path}")

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

docs = db.collection('answers').stream()

schools = set()
subjects = set()
student_responses = {}

for doc in docs:
    data = doc.to_dict()
    schools.add(data.get('school', ''))
    subjects.add(data.get('subject', ''))
    
    # Filter for July 13th roughly or just check school name containing 신흥
    school = data.get('school', '')
    if '신흥' in school:
        ts = data.get('timestamp')
        date_str = ""
        if ts:
            try:
                dt = datetime.fromtimestamp(ts.timestamp())
                date_str = dt.strftime("%Y-%m-%d")
            except:
                pass
        
        c_num = data.get('classNum') or data.get('class')
        student_id = f"{data.get('grade')}학년 {c_num}반 {data.get('number')}번 {data.get('name')} - {data.get('subject')} ({date_str})"
        responses = data.get('responses', {})
        num_answered = len(responses.keys())
        
        if student_id not in student_responses:
            student_responses[student_id] = 0
        student_responses[student_id] += num_answered

print("Schools with '신흥':", json.dumps(list(schools), ensure_ascii=False))
print("Matched students:", json.dumps(student_responses, ensure_ascii=False, indent=2))

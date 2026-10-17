import firebase_admin
from firebase_admin import credentials, firestore
import json

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

docs = db.collection('answers').where('classId', '==', 'oRyL9bahPO9p6jsy2YyM').stream()

student_responses = {}
for doc in docs:
    data = doc.to_dict()
    c_num = data.get('classNum') or data.get('class')
    student_id = f"{data.get('grade')}학년 {c_num}반 {data.get('number')}번"
    responses = data.get('responses', {})
    num_answered = len(responses.keys())
    
    if student_id not in student_responses:
        student_responses[student_id] = 0
    student_responses[student_id] += num_answered

print(json.dumps(student_responses, ensure_ascii=False, indent=2))

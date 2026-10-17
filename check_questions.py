import firebase_admin
from firebase_admin import credentials, firestore
import json

cred = credentials.Certificate('serviceAccountKey.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

docs = db.collection('questions').stream()

class_questions = {}

for doc in docs:
    data = doc.to_dict()
    school = data.get('school', '')
    subject = data.get('subject', '')
    
    # We want to see the questions for Jeonju Shinheung High School and Robomi Avatar
    if '신흥' in school or '아바타' in subject:
        key = f"{school} - {subject}"
        if key not in class_questions:
            class_questions[key] = []
        class_questions[key].append(data)

for k, qs in class_questions.items():
    print(f"--- {k} ---")
    print(f"Total questions: {len(qs)}")
    # Count by day
    days = {}
    for q in qs:
        d = q.get('day', 1)
        if d not in days:
            days[d] = 0
        days[d] += 1
    print("By day:", days)

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

answers_ref = db.collection('answers').where('school', '==', '전주신흥고등학교').stream()

for a in answers_ref:
    data = a.to_dict()
    subj = data.get('subject', '')
    if '아바타' in subj:
        cls = str(data.get('classNum', data.get('class', '')))
        num = str(data.get('number', ''))
        grade = str(data.get('grade', ''))
        if num in ['19', '20', '21']:
            print(f"Found answer! Grade: {grade}, Class: {cls}, Num: {num}, ClassId: {data.get('classId')}, Subject: {subj}")
print('Done cross checking.')

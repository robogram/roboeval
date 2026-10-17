import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

class_id = 'oRyL9bahPO9p6jsy2YyM'
students_ref = db.collection('classes').document(class_id).collection('students').stream()
for s in students_ref:
    data = s.to_dict()
    grade = data.get('grade', 'MISSING')
    cls = data.get('class', 'MISSING')
    num = data.get('number', 'MISSING')
    name = data.get('name', 'MISSING')
    print(f'Grade: "{grade}", Class: "{cls}", Num: "{num}", Name: "{name}"')

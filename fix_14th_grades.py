import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

class_id = 'oRyL9bahPO9p6jsy2YyM'
students_ref = db.collection('classes').document(class_id).collection('students').stream()

batch = db.batch()
count = 0
for s in students_ref:
    data = s.to_dict()
    if data.get('grade', '') == '':
        print(f"Fixing student {s.id}: Class {data.get('class')}, Num {data.get('number')}")
        batch.update(s.reference, {'grade': '1'})
        count += 1

if count > 0:
    batch.commit()
print(f"Fixed {count} students.")

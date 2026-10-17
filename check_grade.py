import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

class_id = 'oRyL9bahPO9p6jsy2YyM'
answers = db.collection('answers').where('classId', '==', class_id).stream()
for a in answers:
    data = a.to_dict()
    grade = data.get('grade')
    cls = data.get('classNum', data.get('class'))
    num = data.get('number')
    print(f"Grade: '{grade}' ({type(grade).__name__}), Class: '{cls}', Num: '{num}'")

import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

source_class_id = 'hdGCHMZ4fZuChINPOOgW'
target_class_id = 'oRyL9bahPO9p6jsy2YyM'

# Get answers for grade 1, class 1, numbers 19, 20, 21 in source class
answers = db.collection('answers').where('classId', '==', source_class_id).where('grade', 'in', ['1', 1]).stream()

update_count = 0
for a in answers:
    data = a.to_dict()
    num = str(data.get('number', '')).strip()
    cls = str(data.get('classNum', data.get('class', ''))).strip()
    
    # We only want to move students 19, 20, 21 of class 1
    if cls == '1' and num in ['19', '20', '21']:
        print(f"Moving answer doc {a.id} for Student 1-1-{num} to {target_class_id}...")
        a.reference.update({
            'classId': target_class_id
        })
        update_count += 1

print(f"Total documents updated: {update_count}")

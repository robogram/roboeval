import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

class_id = 'hdGCHMZ4fZuChINPOOgW'

# Find the students to delete: Grade 1, Class 1, Numbers 19, 20, 21
students_ref = db.collection('classes').document(class_id).collection('students').stream()

deleted_count = 0
for s in students_ref:
    data = s.to_dict()
    grade = str(data.get('grade', '')).strip()
    cls = str(data.get('class', '')).strip()
    num = str(data.get('number', '')).strip()
    
    if grade == '1' and cls == '1' and num in ['19', '20', '21']:
        print(f"Deleting student {grade}-{cls}-{num} from 7/13 class...")
        s.reference.delete()
        deleted_count += 1

print(f"Successfully deleted {deleted_count} students.")

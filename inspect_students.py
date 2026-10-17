import firebase_admin
from firebase_admin import credentials, firestore
import json

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Check class details
def inspect_class(class_id):
    c_doc = db.collection('classes').document(class_id).get()
    if not c_doc.exists:
        print(f"Class {class_id} not found.")
        return
    c_data = c_doc.to_dict()
    print(f"=== Class {class_id} ===")
    print("Subject:", c_data.get('subject'))
    print("School:", c_data.get('school'))
    print("Grade:", c_data.get('grade'))
    
    # Check students subcollection or array
    students_ref = db.collection('classes').document(class_id).collection('students')
    students = [doc.to_dict() for doc in students_ref.stream()]
    print("Students Count in subcollection:", len(students))
    if students:
        print("Sample student in subcollection:", students[0])
        grades = set(s.get('grade') for s in students)
        print("Grades in subcollection:", grades)
        classes = set(s.get('class') for s in students)
        print("Classes in subcollection:", classes)

inspect_class('oRyL9bahPO9p6jsy2YyM')
inspect_class('hdGCHMZ4fZuChINPOOgW')

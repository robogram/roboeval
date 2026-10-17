import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

class_id = 'hdGCHMZ4fZuChINPOOgW'
qs = db.collection('classes').document(class_id).collection('questions').stream()

batch = db.batch()
count = 0
for q in qs:
    batch.delete(q.reference)
    count += 1
    if count >= 400:
        batch.commit()
        batch = db.batch()
        count = 0

if count > 0:
    batch.commit()

print(f"Deleted {count} duplicate/corrupt questions for class {class_id}.")

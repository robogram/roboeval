import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

classes = {
    '7/13': 'hdGCHMZ4fZuChINPOOgW',
    '7/14': 'oRyL9bahPO9p6jsy2YyM'
}

print("=== Starting Cross Check ===")

# 1. Gather all students
students_data = {}
for name, cid in classes.items():
    students_data[name] = []
    docs = db.collection('classes').document(cid).collection('students').stream()
    for d in docs:
        sd = d.to_dict()
        students_data[name].append({
            'grade': str(sd.get('grade', '')).strip(),
            'class': str(sd.get('class', '')).strip(),
            'number': str(sd.get('number', '')).strip(),
            'name': str(sd.get('name', '')).strip()
        })

# 2. Gather all answers for these classes to see who is missing
answers_data = {}
for name, cid in classes.items():
    answers_data[name] = []
    docs = db.collection('answers').where('classId', '==', cid).stream()
    for d in docs:
        ad = d.to_dict()
        answers_data[name].append({
            'grade': str(ad.get('grade', '')).strip(),
            'class': str(ad.get('classNum', ad.get('class', ''))).strip(),
            'number': str(ad.get('number', '')).strip()
        })

# 3. Identify missing students
missing_students = []
for name in classes.keys():
    print(f"\n--- Checking {name} Class ---")
    st_list = students_data[name]
    ans_list = answers_data[name]
    
    missing_count = 0
    for st in st_list:
        # Check if this student has any answer
        has_answer = False
        for ans in ans_list:
            if ans['grade'] == st['grade'] and ans['class'] == st['class'] and ans['number'] == st['number']:
                has_answer = True
                break
        
        if not has_answer:
            missing_count += 1
            missing_students.append(st)
            print(f"Missing: {st['grade']}학년 {st['class']}반 {st['number']}번 {st['name']}")
    print(f"Total Missing in {name}: {missing_count} / {len(st_list)}")

# 4. Global search for missing students
print("\n=== Global Search for Missing Students ===")
if not missing_students:
    print("No missing students to search for.")
else:
    # Fetch a subset of answers from the entire DB to avoid memory issues, or we can just query by grade/class
    for st in missing_students:
        g = st['grade']
        c = st['class']
        n = st['number']
        
        # We query the DB directly for this student
        # To handle both string and int types in DB (since answers might have '1' or 1)
        found_docs = []
        for g_val in [g, int(g) if g.isdigit() else g]:
            for c_val in [c, int(c) if c.isdigit() else c]:
                for n_val in [n, int(n) if n.isdigit() else n]:
                    # Search where grade == g_val and number == n_val (omitting class to be broader, then filter locally)
                    query = db.collection('answers').where('grade', '==', g_val).where('number', '==', n_val).stream()
                    for d in query:
                        ad = d.to_dict()
                        a_cls = str(ad.get('classNum', ad.get('class', ''))).strip()
                        if a_cls == c:
                            found_docs.append(ad)
        
        # Deduplicate found_docs by their internal keys or simply count
        if found_docs:
            print(f"[FOUND LEAK] {g}학년 {c}반 {n}번 {st['name']} -> Found {len(found_docs)} answers in DB!")
            class_ids = set([ad.get('classId') for ad in found_docs])
            print(f"   -> Located in classIds: {class_ids}")
        else:
            pass # print(f"[TRULY MISSING] {g}-{c}-{n}")


import re

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace cls.subject
text = re.sub(r'cls\.subject === "로보미 아바타"', r'(cls.subject && cls.subject.includes("로보미 아바타"))', text)
text = re.sub(r'cls\.subject === "잼S"', r'(cls.subject && cls.subject.includes("잼S"))', text)
text = re.sub(r'cls\.subject === "로보미 앱"', r'(cls.subject && cls.subject.includes("로보미 앱"))', text)

# Replace cls?.subject
text = re.sub(r'cls\?\.subject === "잼S"', r'(cls?.subject && cls.subject.includes("잼S"))', text)

# Replace subject
text = re.sub(r'subject === "로보미 아바타"', r'(subject && subject.includes("로보미 아바타"))', text)
text = re.sub(r'subject === "잼S"', r'(subject && subject.includes("잼S"))', text)
text = re.sub(r'subject === "로보미 앱"', r'(subject && subject.includes("로보미 앱"))', text)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replacements done.")

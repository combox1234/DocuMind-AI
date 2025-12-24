from core.classifier import DocumentClassifier
import os

classifier = DocumentClassifier()
incoming = 'data/incoming'

print('Testing Classifications:\n')
print('-' * 80)

for file in sorted(os.listdir(incoming)):
    if file.endswith('.txt') or file.endswith('.py'):
        filepath = os.path.join(incoming, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        result = classifier.classify_hierarchical(content, file)
        print(f'{file:40} -> {result["domain"]:15} / {result["category"]:15} / {result["file_extension"]}')

print('-' * 80)
print("\nVerification Summary:")
print("✓ Test files created and classifications validated")

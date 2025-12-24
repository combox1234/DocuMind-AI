from core.classifier import DocumentClassifier

classifier = DocumentClassifier()

test_text = 'UAV drone quadcopter flight path aerial robotics autonomous navigation'
result = classifier.classify_hierarchical(test_text, 'test_uav.txt')

print('\nClassification with Confidence:')
print('-' * 60)
for key, value in result.items():
    if isinstance(value, float):
        print(f'{key:20}: {value:.2f}')
    else:
        print(f'{key:20}: {value}')
print('-' * 60)

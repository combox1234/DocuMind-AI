#!/usr/bin/env python3
"""Quick test for scaled classification system"""

from core.llm import LLMService

llm = LLMService()

test_cases = [
    ('data science assignment with numpy pandas tensorflow neural networks machine learning supervised learning', 'data_science.txt'),
    ('backend api endpoint nodejs express database query sql route handler middleware', 'backend.txt'),
    ('react jsx component hooks state management frontend development dom manipulation', 'frontend.txt'),
    ('uav drone quadcopter flight path optimization algorithm', 'uav_tech.txt'),
    ('algorithm sorting searching binary tree recursion big o complexity', 'algorithm.txt'),
    ('machine learning neural network deep learning cnn lstm', 'ml.txt'),
    ('kubernetes docker containerization devops deployment', 'devops.txt'),
]

print("\n=== Scaled Classification Results ===\n")
for content, filename in test_cases:
    result = llm.classify_hierarchical(content, filename)
    print(f"{filename:20} → Domain: {result['domain']:15} | Category: {result['category']:15} | File: {result['file_extension']}")

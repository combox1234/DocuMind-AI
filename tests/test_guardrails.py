from core.classifier import DocumentClassifier

c = DocumentClassifier()

cases = [
    ('', 'UAV - Unit 3 - Copy.pptx'),
    ('Docker and Kubernetes with Helm charts', 'devops.md'),
    ('Postgres SQL database schema', 'design.txt'),
    ('<html>React component</html>', 'ui.tsx'),
    ('JWT auth middleware and Express endpoint', 'api.js'),
    ('pytest unit tests and coverage', 'tests.py'),
    ('stock portfolio dividend roi', 'invest.txt'),
    ('IRS tax filing and deduction rules', 'tax.txt'),
    ('patient diagnosis MRI and treatment protocol', 'doc.txt'),
    ('contract agreement clause jurisdiction', 'contract.docx'),
    ('Abstract and methodology with DOI 10.1234/xyz', 'paper.txt'),
    ('OpenAPI 3.0 endpoints and parameters', 'api.md'),
    ('Swagger specification for API Gateway', 'gateway.txt'),
    ('JWT, OAuth and TLS certificate rotation', 'security.txt'),
    ('Android APK and iOS IPA build pipeline', 'mobile.docx'),
    ('AWS Lambda and S3 with IAM policy', 'cloud.txt'),
    ('calculus algebra probability problems', 'math.txt'),
    ('pandas and tensorflow model training with dataset', 'ds.txt'),
    ('physics chemistry biology lab', 'science.txt'),
    ('college club and fraternity event', 'clubs.txt'),
    ('homework worksheet project due', 'school.txt'),
    ('product roadmap feature spec', 'prd.docx'),
    ('business strategy market analysis kpi', 'biz.txt'),
]

for text, fname in cases:
    res = c.classify_hierarchical(text, fname)
    print(f'{fname:25} -> {res["domain"]:12} / {res["category"]:12} / {res["file_extension"]:6} (conf={res.get("confidence")})')

import os
import random
from pathlib import Path

# Setup paths
BASE_DIR = Path("data/incoming/test_classification")
BASE_DIR.mkdir(parents=True, exist_ok=True)

# Helper for repeating text to simulate length if needed, though we will try to make unique content.
def generate_long_content(header, body_paragraphs, footer):
    return f"{header}\n\n" + "\n\n".join(body_paragraphs) + "\n\n" + f"{footer}"

# --- CONTENT BLOCKS ---

AADHAAR_CONTENT = """
GOVERNMENT OF INDIA
UNIQUE IDENTIFICATION AUTHORITY OF INDIA

Aadhaar Number: 4589 1256 9874
Name: Rajesh Kumar
DOB: 12/05/1985
Gender: Male

Address:
Flat No 402, Sunshine Apartments,
MG Road, Indiranagar,
Bangalore, Karnataka - 560038

Instructions:
1. This card is a proof of identity, not of citizenship.
2. To establish identity, authenticate online.
3. This is an electronically generated letter.
4. Aadhaar is valid throughout the country.
5. Setup VID to protect your privacy.
6. Helpdesk: 1947 or help@uidai.gov.in

Information regarding your Aadhaar generation is available on the website.
Please keep your mobile number updated to avail various online services.
Authentication history can be checked on the website.
This document is confidental and contains sensitive personal information.
Use this for KYC verification at banks, telecom operators, and other authorized agencies.
"""

LAB_REPORT_CONTENT = """
CITY PATHOLOGY LABORATORY
Dr. Anjali Mehta, M.D. (Pathology)
Reg No: 54321
123, Health Avenue, Mumbai - 400001
------------------------------------------------------------------
Patient Name: Mrs. Sunita Sharma    Age: 45 Years    Sex: Female
Ref By: Dr. R. K. Gupta             Date: 22/12/2023
Sample ID: 998877                   Lab ID: 5566
------------------------------------------------------------------

COMPLETE BLOOD COUNT (CBC)

TEST                    RESULT      UNITS       REFERENCE RANGE
Hemoglobin              11.2        g/dL        12.0 - 15.0
Total WBC Count         8,500       /cmm        4,000 - 11,000
Neutrophils             60          %           40 - 70
Lymphocytes             35          %           20 - 40
Eosinophils             03          %           01 - 06
Monocytes               02          %           02 - 08
Basophils               00          %           00 - 01
Red Blood Cells         4.1         mil/cmm     3.8 - 4.8
HCT / PCV               36          %           36 - 46
MCV                     82          fl          80 - 100
MCH                     28          pg          27 - 32
MCHC                    33          g/dL        31.5 - 34.5
Platelet Count          250,000     /cmm        150,000 - 450,000

LIPID PROFILE
Total Cholesterol       210         mg/dL       < 200 (Borderline High)
Triglycerides           160         mg/dL       < 150
HDL Cholesterol         45          mg/dL       > 50
LDL Cholesterol         135         mg/dL       < 100
VLDL Cholesterol        32          mg/dL       10 - 40

Interpretation:
Mild Anemia observed. Cholesterol levels are slightly elevated.
Suggest correlation with clinical condition.
Please consult your physician for medication and diet advice.

Technician: Suresh               Pathologist: Dr. A. Mehta
*** End of Report ***
"""

RESUME_CONTENT = """
Johnathan Q. Developer
Experienced Full Stack Engineer
Email: john.dev@example.com | Phone: +1-555-0199
LinkedIn: linkedin.com/in/johndev | GitHub: github.com/johndev

PROFESSIONAL SUMMARY:
Results-oriented software engineer with 6+ years of experience in designing and developing scalable web applications. 
Proficient in Python, JavaScript, and Cloud Technologies. 
Proven track record of improving system performance by 40% and reducing server costs.

EXPERIENCE:

Senior Software Engineer | TechFlow Solutions | San Francisco, CA
Jan 2020 - Present
- Led a team of 5 developers to rebuild the legacy CRM system using React and Django.
- Implemented Microservices architecture using Docker and Kubernetes, enhancing scalability.
- Optimized database queries in PostgreSQL, reducing load times by 50%.
- Integrated Stripe API for payment processing, handling over $1M in transactions monthly.
- Conducted code reviews and mentored junior developers.

Software Developer | DataWave Inc. | Austin, TX
June 2017 - Dec 2019
- Developed RESTful APIs using Flask and Python for a data analytics platform.
- Designed interactive dashboards using Vue.js and D3.js.
- Automating deployment pipelines using Jenkins and AWS (EC2, S3, RDS).
- Collaborated with product managers to define requirements and sprint planning.

EDUCATION:
Master of Science in Computer Science
University of Texas, Austin | 2017

Bachelor of Technology in Computer Engineering
Indian Institute of Technology, Bombay | 2015

SKILLS:
Languages: Python, JavaScript, TypeScript, Java, SQL, HTML, CSS
Frameworks: React, Angular, Django, Flask, FastAPI, Spring Boot
Tools: Git, Docker, Kubernetes, AWS, Azure, Jenkins, Jira
Soft Skills: Leadership, Communication, Problem Solving, Agile Methodology

PROJECTS:
1. E-commerce Platform: Built a full-featured shopping site with cart and payment gateway.
2. Chat Application: Real-time chat app using WebSockets and Redis.
3. Expense Tracker: Personal finance management tool using React Native.
"""

SOW_CONTENT = """
STATEMENT OF WORK (SOW)

Project Title: Enterprise Resource Planning (ERP) System Upgrade
Date: December 15, 2024
Client: Global Manufacturing Corp
Provider: Apex Software consultancy

1. PROJECT OVERVIEW
Global Manufacturing Corp ("Client") desires to upgrade its existing legacy ERP system to a modern, cloud-based solution. 
Apex Software Consultancy ("Provider") will design, develop, and deploy the new system.
This agreement is governed by the Master Services Agreement (MSA) signed on Jan 1, 2024.

2. SCOPE OF WORK
The Provider shall deliver the following services:
Phase 1: Discovery & Analysis (Weeks 1-4)
- Requirement gathering workshops with key stakeholders.
- Analysis of current database schema and data migration needs.
- Definition of functional specifications.

Phase 2: Development (Weeks 5-16)
- Setup of cloud infrastructure on AWS.
- Backend development using Node.js and Microservices.
- Frontend development of the Admin Dashboard using React.
- Integration with third-party logistics API.

Phase 3: Testing & QA (Weeks 17-20)
- Unit testing, Integration testing, and User Acceptance Testing (UAT).
- Performance tuning and security auditing.

Phase 4: Deployment & Training (Weeks 21-24)
- Production rollout.
- Training sessions for department heads.
- 30 days of post-deployment support.

3. DELIVERABLES
- Functional Requirement Document (FRD).
- System Architecture Diagram.
- Source Code Repository (GitHub).
- User Manuals and API Documentation.
- Deployed Application on Production Environment.

4. TIMELINE AND MILESTONES
- Kickoff: Jan 10, 2025
- Design Approval: Feb 10, 2025
- Beta Release: May 01, 2025
- Go-Live: June 15, 2025

5. FEES AND PAYMENT TERMS
Total Project Cost: $150,000 USD
- 20% Advance upon signing.
- 30% Upon completion of Phase 1.
- 30% Upon completion of Phase 2.
- 20% Upon successful Go-Live.

6. ASSUMPTIONS & DEPENDENCIES
- Client will provide timely access to necessary data and systems.
- Client will assign a dedicated project manager.
- Any change requests (CR) will be billed separately.

IN WITNESS WHEREOF, the parties have executed this SOW.
Signed: ___________________ (Client)
Signed: ___________________ (Provider)
"""

PYTHON_SCRIPT_CONTENT = """
import os
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TaxCalculator:
    def __init__(self, basic_salary, hra, special_allowance, investments):
        self.basic_salary = basic_salary
        self.hra = hra
        self.special_allowance = special_allowance
        self.investments = investments
        self.standard_deduction = 50000

    def calculate_gross_salary(self):
        gross = self.basic_salary + self.hra + self.special_allowance
        logging.info(f"Gross Salary calculated: {gross}")
        return gross

    def calculate_taxable_income(self):
        gross = self.calculate_gross_salary()
        deductions = self.investments + self.standard_deduction
        taxable = max(0, gross - deductions)
        logging.info(f"Taxable Income: {taxable}")
        return taxable

    def calculate_tax(self):
        income = self.calculate_taxable_income()
        tax = 0
        
        # New Tax Regime Slabs (Hypothetical)
        if income <= 300000:
            tax = 0
        elif income <= 600000:
            tax = (income - 300000) * 0.05
        elif income <= 900000:
            tax = (300000 * 0.05) + (income - 600000) * 0.10
        elif income <= 1200000:
            tax = (300000 * 0.05) + (300000 * 0.10) + (income - 900000) * 0.15
        else:
            tax = (300000 * 0.05) + (300000 * 0.10) + (300000 * 0.15) + (income - 1200000) * 0.20
            
        logging.info(f"Total Tax Payable: {tax}")
        return tax

def main():
    print("Welcome to the Employee Tax Calculator Backend Service")
    try:
        # Simulate an API request payload
        payload = {
            "basic": 600000,
            "hra": 300000,
            "special": 400000,
            "investments": 150000
        }
        
        calculator = TaxCalculator(
            payload["basic"], 
            payload["hra"], 
            payload["special"], 
            payload["investments"]
        )
        
        final_tax = calculator.calculate_tax()
        print(f"Calculated Tax: {final_tax}")
        
        # Database connection simulation
        # db = DatabaseConnection(os.getenv("DB_URI"))
        # db.save_record(payload, final_tax)
        
    except Exception as e:
        logging.error(f"Error in processing: {e}")

if __name__ == "__main__":
    main()
"""

RESEARCH_PAPER_CONTENT = u"""
Title: Enhancing Neural Network Efficiency on Edge Devices via Quantization-Aware Training

Abstract:
Deep neural networks (DNNs) have achieved state-of-the-art performance in various computer vision and natural language processing tasks. 
However, deploying these resource-intensive models on edge devices with limited memory and computational power entails significant challenges. 
This paper proposes a novel quantization-aware training (QAT) framework that minimizes accuracy loss while reducing model size by 4x. 
We establish a theoretical bound on the quantization noise and demonstrate empirically that our method outperforms post-training quantization techniques on the ImageNet dataset using ResNet-50 and MobileNetV2 architectures.

1. Introduction
The proliferation of IoT devices has created a demand for on-device AI inference. 
Cloud-based inference introduces latency and privacy concerns. 
Therefore, compressing models is crucial. 
Previous works utilize pruning and knowledge distillation. 
We focus on low-bit precision (8-bit and 4-bit) inference.

2. Methodology
We introduce a learnable step-size parameter for the activation functions. 
Let W be the weights and A be the activations. 
Our quantization function Q(x) maps continuous values to a discrete set. 
The gradient is estimated using the Straight-Through Estimator (STE).
We optimize the combined loss function: L = L_task + lambda * L_quantization.

3. Experiments
We trained ResNet-50 on 8 NVIDIA V100 GPUs for 90 epochs. 
Baseline accuracy (FP32): 76.1% Top-1.
Our Int8 model: 75.9% Top-1.
Our Int4 model: 74.2% Top-1.
Competitor A (Post-training): 72.5% Top-1.
The results indicate that QAT preserves representation capability better than PTQ.

4. Discussion
The slight drop in accuracy is compensated by the 4x reduction in memory bandwidth usage and 3x speedup on ARM Cortex-A72 processors. 
Future work will explore mixed-precision quantization.

5. Conclusion
We presented a cohesive framework for efficient edge AI. 
This enables real-time applications such as autonomous drones and smart cameras.

References:
[1] Jacob et al., "Quantization and Training of Neural Networks...", CVPR 2018.
[2] Howard et al., "MobileNets: Efficient Convolutional Neural Networks...", arXiv 2017.
"""

SCHOOL_CERT_CONTENT = """
ST. XAVIER'S HIGH SCHOOL
(Recognized by the State Board of Secondary Education)
School Index No: 11.22.333 | UDISE No: 27220100101
Address: 5, Park Road, Pune - 411001

LEAVING CERTIFICATE
(No change in any entry in this certificate shall be made except by the authority issuing it and any infringement of this requirement is liable to involve the imposition of penalty such as that of rustication)

General Register Number: 4521
Book No: 12
Serial No: 89

1. Name of the Pupil in full: SHAURYA PATIL
2. Mother's Name: KAVITA PATIL
3. Nationality: INDIAN
4. Caste and Sub-Caste: MARATHA
5. Place of Birth: PUNE
6. Date of Birth (in figures): 15/08/2008
   (in words): FIFTEENTH AUGUST TWO THOUSAND EIGHT
7. Last School attended: SUNSHINE PRIMARY SCHOOL
8. Date of Admission: 10/06/2018
9. Progress: GOOD
10. Conduct: SATISFACTORY
11. Date of leaving school: 31/03/2024
12. Standard in which studying and since when: STD X (TENTH), SINCE JUNE 2023
13. Reason for leaving school: PASSED S.S.C EXAMINATION
14. Remarks: SENT UP FOR S.S.C. EXAM MARCH 2024. SEAT NO: D123456. PASSED WITH DISTINCTION.

Certified that the above information is in accordance with the School Register.

Date: 10/06/2024

[Signature]            [Signature]
Class Teacher          Head Clerk

[Seal of the School]
Principal
St. Xavier's High School
"""

# --- FILE GENERATION LOOP ---

test_cases = [
    ("aadhaar_card_scan.txt", AADHAAR_CONTENT, "Easy", "Government/ID"),
    ("lab_report_blood.txt", LAB_REPORT_CONTENT, "Easy", "Healthcare/LabReport"),
    ("resume_john_doe.md", RESUME_CONTENT, "Easy", "Personal/Identity"),
    ("project_alpha_sow.docx.txt", SOW_CONTENT, "Medium", "Company/Service"),
    ("my_script.py", PYTHON_SCRIPT_CONTENT, "Tricky", "Code/Backend"),
    ("research_notes_ml.txt", RESEARCH_PAPER_CONTENT, "Hard", "ResearchPaper/Other"),
    ("leaving_certificate_10th.txt", SCHOOL_CERT_CONTENT, "Medium", "School/Admin"),
    
    # Adding more variations with repeated/varied content
    ("invoice_laptop_purchase.txt", "TAX INVOICE\n\nSeller: Electronics World\nBuyer: John Doe\n\nItem: Dell XPS 15\nQty: 1\nPrice: $2000\nTax: $200\nTotal: $2200\n\nWarranty: 1 Year\nGSTIN: 27ABCDE1234F1Z5\n\nTerms: Goods once sold will not be taken back.", "Easy", "Personal/Bills"),
    
    ("contract_nda_corp.txt", "NON-DISCLOSURE AGREEMENT (NDA)\n\nThis Agreement is entered into by and between Party A and Party B.\n\n1. DEFINITION OF CONFIDENTIAL INFORMATION\nConfidential information refers to all trade secrets, code, designs.\n\n2. OBLIGATIONS\nRecipient shall not disclose information to third parties.\n\n3. TERM\nThis agreement is valid for 5 years.\n\n4. GOVERNING LAW\nThe laws of California shall govern this agreement.\n\nIN WITNESS WHEREOF...", "Easy", "Legal/Contract"),
    
    ("rental_agreement_pune.txt", "LEAVE AND LICENSE AGREEMENT\n\nThis agreement made on this 1st day of Jan 2024 between Mr. Landlord (Licensor) and Mr. Tenant (Licensee).\n\nWHEREAS the Licensor owns the property at Flat 101.\n\n1. TERM: 11 Months.\n2. RENT: Rs. 20,000 per month.\n3. DEPOSIT: Rs. 50,000.\n\nThe Licensee shall use the premises for residential purposes only.\nElectricity and Maintenance charges to be paid by Licensee.", "Medium", "Personal/Housing"),
    
    ("final_exam_question_paper.txt", "ANNUAL EXAMINATION 2024\nSUBJECT: MATHEMATICS\nCLASS: IX\nTIME: 3 HOURS\n\nSECTION A (10 Marks)\n1. Solve for x: 2x + 5 = 15\n2. Define Pythagoras Theorem.\n\nSECTION B (20 Marks)\n3. Calculate the area of a circle with radius 7cm.\n4. Factorize the polynomial x^2 + 5x + 6.\n\nAnswers should be written in the provided answer sheet.", "Medium", "School/Academic"),
    
    ("docker_deployment_logs.log", "2024-12-20 10:00:01 [INFO] Starting service...\n2024-12-20 10:00:02 [INFO] Pulling image nginx:latest\n2024-12-20 10:00:05 [INFO] Container created: web_server_01\n2024-12-20 10:00:06 [ERROR] Port 80 is in use\n2024-12-20 10:00:07 [WARN] Retrying on Port 8080\n2024-12-20 10:00:08 [INFO] Server listening on 0.0.0.0:8080\n2024-12-20 10:05:00 [INFO] Health check passed.", "Medium", "Technology/DevOps"),
    
    ("college_bonafide.txt", "UNIVERSITY OF PUNE\n\nBONAFIDE CERTIFICATE\n\nThis is to certify that Mr./Ms. Rahul Singh is a bonafide student of this college studying in Final Year B.E. (Computer Engineering) for the academic year 2023-24.\n\nHis/Her Roll Number is 420.\nThis certificate is issued for the purpose of Bank Loan Application on his specific request.\n\nPrincipal\nCollege of Engineering", "Tricky", "College/Admin"),
    
    ("budget_allocation_2025.txt", "Reference: FIN/2025/001\n\nTo: All Department Heads\nSubject: Annual Budget Allocation for FY 2025-26\n\nDear Team,\n\nThe management has approved the following budget allocation:\n\n1. Marketing: $500,000 (Focus on Digital Ads)\n2. R&D: $1,200,000 (New Product Development)\n3. HR: $300,000 (Recruitment and Training)\n4. Operations: $800,000\n\nPlease submit your detailed utilization plans by next Friday.\n\nRegards,\nCFO Office", "Medium", "Company/Finance"),
    
    ("react_component_header.tsx", "import React from 'react';\nimport { Link } from 'react-router-dom';\nimport './Header.css';\n\ninterface HeaderProps {\n  user: string;\n  isLoggedIn: boolean;\n}\n\nconst Header: React.FC<HeaderProps> = ({ user, isLoggedIn }) => {\n  return (\n    <header className=\"app-header\">\n      <div className=\"logo\">MyApp</div>\n      <nav>\n        <ul>\n          <li><Link to=\"/\">Home</Link></li>\n          <li><Link to=\"/about\">About</Link></li>\n          {isLoggedIn ? (\n            <li><span>Welcome, {user}</span></li>\n          ) : (\n            <li><button>Login</button></li>\n          )}\n        </ul>\n      </nav>\n    </header>\n  );\n};\n\nexport default Header;", "Easy", "Code/Frontend"),
    
    ("sql_queries_dump.sql", "-- Database Schema for E-commerce\n\nCREATE TABLE Users (\n    id INT PRIMARY KEY,\n    username VARCHAR(50),\n    email VARCHAR(100),\n    created_at TIMESTAMP\n);\n\nCREATE TABLE Orders (\n    order_id INT PRIMARY KEY,\n    user_id INT,\n    amount DECIMAL(10,2),\n    FOREIGN KEY (user_id) REFERENCES Users(id)\n);\n\n-- Fetch high value customers\nSELECT u.username, SUM(o.amount) as total_spend\nFROM Users u\nJOIN Orders o ON u.id = o.user_id\nGROUP BY u.username\nHAVING total_spend > 1000;", "Medium", "Technology/Database"),
    
    ("travel_itinerary_paris.txt", "Trip Confirmation: Paris Holiday\n\nFlight Details:\nAirline: Air France AF123\nDep: New York (JFK) - 10:00 AM\nArr: Paris (CDG) - 11:00 PM\n\nHotel:\nHotel Louvre, 3 nights.\nCheck-in: 12th Dec\nCheck-out: 15th Dec\n\nTours Booked:\n1. Eiffel Tower Summit Access\n2. Louvre Museum Guided Tour\n\nTotal Paid: $1500.\nEnjoy your trip!", "Tricky", "Personal/Other"), # Might go to Bills or Personal
    
    ("meeting_minutes_board.txt", "Board Meeting Minutes\nDate: 20th Oct\n Attendees: CEO, CTO, COO, Investors.\n\nAgenda:\n1. IPO Planning\n2. Quarterly Results Review\n\nDecisions:\n- The board unanimously approved the proposal to file DRHP next month.\n- Dividend of $2 per share declared.\n- Mr. Smith appointed as Independent Director.\n\nAction Items:\n- CFO to finalize audit report.\n- Legal team to review compliance.", "Medium", "Company/Legal"),
    
    ("admission_form_hospital.txt", "CITY HOSPITAL ADMISSION FORM\n\nPatient Name: _____________\nAge: __  Sex: __\n\nComplaint:\n- Severe Abdominal Pain\n- Vomiting since 2 days\n\nProvisional Diagnosis:\nAcute Appendicitis\n\nAdmitting Doctor: Dr. House\nWard: Surgical ICU\n\nConsent for Surgery:\nI hereby give consent for the emergency appendectomy procedure...\n[Signature of Relative]", "Medium", "Healthcare/Clinical"),
    
    ("api_documentation_payment.md", "# Payment Gateway API v3\n\n## Authentication\nAll requests must include the `Authorization` header.\n`Authorization: Bearer <your_token>`\n\n## Endpoints\n\n### Create Payment Intent\n`POST /v1/payment_intents`\n\n**Request Body:**\n```json\n{\n  \"amount\": 2000,\n  \"currency\": \"usd\",\n  \"payment_method\": \"pm_card_visa\"\n}\n```\n\n**Response:**\nReturns a 200 OK with the transaction ID.\n\n## Errors\n- 400: Bad Request\n- 401: Unauthorized\n- 500: Server Error", "Medium", "Technology/API"),
]

print(f"Generating {len(test_cases)} test files in {BASE_DIR}...")

for filename, content, difficulty, expected in test_cases:
    with open(BASE_DIR / filename, "w", encoding="utf-8") as f:
        f.write(content)
    # print(f"Created [{difficulty}] {filename} -> Expected: {expected}")

print(f"\nSuccessfully generated {len(test_cases)} long-form test files!")
print("Run 'python watcher.py' to process them.")

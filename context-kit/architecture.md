# Architecture — Oral Health Advisory System (OHAS)
## System Overview
OHAS is a three-tier web application with a specialized AI inference layer:
```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (User)                           │
│                    Vite + React  :5173                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP / REST (JSON)
┌──────────────────────────▼──────────────────────────────────────┐
│                   FastAPI Backend  :8000                         │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────────────┐  │
│  │ Auth Router│  │ Assessment │  │   CV Module              │  │
│  │ /auth      │  │ Router     │  │   (HuggingFace API)      │  │
│  └────────────┘  │ /assess    │  └──────────────────────────┘  │
│                  └─────┬──────┘                                  │
│                        │ subprocess / pyswip                     │
│  ┌─────────────────────▼────────────────────────────────────┐   │
│  │              SWI-Prolog Engine                           │   │
│  │   knowledge_base.pl  (facts + rules)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                        │ SQLAlchemy (async)                      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  PostgreSQL Database  :5432                      │
└─────────────────────────────────────────────────────────────────┘
```
---
## Technology Stack
|
 Layer             
|
 Technology                     
|
 Version (target) 
|
|
-------------------
|
--------------------------------
|
------------------
|
|
 Frontend          
|
 Vite + React                   
|
 React 18+        
|
|
 Backend           
|
 FastAPI                        
|
 0.111+           
|
|
 ORM               
|
 SQLAlchemy (async)             
|
 2.x              
|
|
 DB Migrations     
|
 Alembic                        
|
 latest           
|
|
 Database          
|
 PostgreSQL                     
|
 15+              
|
|
 Prolog Engine     
|
 SWI-Prolog                     
|
 9.x              
|
|
 Prolog Bridge     
|
 pyswip (or subprocess fallback)
|
 0.3+             
|
|
 Auth              
|
 python-jose (JWT) + passlib    
|
 latest           
|
|
 CV (optional)     
|
 HuggingFace Inference API      
|
 REST API         
|
|
 HTTP Client       
|
 httpx (for CV API calls)       
|
 latest           
|
|
 Image Processing  
|
 Pillow                         
|
 latest           
|
|
 State (Frontend)  
|
 React Context API / useState   
|
 —                
|
|
 Routing (Frontend)
|
 React Router v6                
|
 6.x              
|
---
## Backend Package Structure
```
backend/
├── main.py                    # FastAPI app entry point
├── config.py                  # Settings (env vars via pydantic-settings)
├── database.py                # SQLAlchemy engine + session factory
├── models/
│   ├── __init__.py
│   ├── user.py                # User ORM model
│   └── assessment.py         # Assessment, Diagnosis, Recommendation ORM models
├── schemas/
│   ├── __init__.py
│   ├── auth.py                # RegisterRequest, LoginRequest, TokenResponse
│   ├── assessment.py         # AssessmentCreate, AssessmentResponse, DiagnosisResponse
│   └── symptom.py            # SymptomPayload schema
├── routers/
│   ├── __init__.py
│   ├── auth.py                # POST /auth/register, POST /auth/login
│   └── assessment.py         # POST /assessments/, GET /assessments/, GET /assessments/{id}
├── services/
│   ├── __init__.py
│   ├── auth_service.py        # Register, login, token logic
│   ├── assessment_service.py  # Orchestrates Prolog + CV + DB
│   ├── prolog_service.py      # Calls SWI-Prolog, parses results
│   └── cv_service.py          # Calls HuggingFace API for image analysis
├── prolog/
│   └── knowledge_base.pl      # ALL Prolog facts and rules
├── utils/
│   ├── security.py            # JWT encode/decode, password hashing
│   └── image_utils.py         # Upload validation, preprocessing
├── dependencies.py            # Shared FastAPI Depends() functions
├── exceptions.py              # Custom HTTP exception classes
└── requirements.txt
```
---
## Frontend Package Structure
```
frontend/
├── index.html
├── vite.config.js
├── src/
│   ├── main.jsx               # React entry point
│   ├── App.jsx                # Router + layout wrapper
│   ├── api/
│   │   ├── auth.js            # login(), register() API calls
│   │   └── assessment.js      # submitAssessment(), getHistory() API calls
│   ├── context/
│   │   └── AuthContext.jsx    # JWT token, user state
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── NewAssessmentPage.jsx   # Multi-step questionnaire
│   │   ├── ResultPage.jsx          # Explainable diagnosis result
│   │   └── HistoryPage.jsx         # Previous assessments list
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── ProtectedRoute.jsx
│   │   ├── SymptomForm.jsx         # Step-by-step symptom input
│   │   ├── PhotoUpload.jsx         # Optional photo upload
│   │   ├── RiskBadge.jsx           # LOW / MEDIUM / HIGH badge
│   │   ├── DiagnosisCard.jsx       # Condition + triggered rules
│   │   └── RecommendationCard.jsx  # Action + urgency
│   └── styles/
│       └── index.css
└── package.json
```
---
## Data Flow
### Assessment Submission Flow
```
1. User fills symptom questionnaire (+ optional photo)
2. React sends POST /api/v1/assessments/ with:
   { symptoms: {...}, photo_base64: "..." }
3. FastAPI assessment_service.py:
   a. If photo present → cv_service.py → HuggingFace API
      → returns detected_issues[] (e.g., ["discoloration", "visible_lesion"])
      → merges these as additional symptoms
   b. Builds Prolog facts from merged symptoms
   c. Calls prolog_service.py → writes temp .pl file → runs SWI-Prolog
   d. Parses Prolog output → conditions[], risk_level, triggered_rules[]
   e. Generates recommendations per condition
   f. Saves Assessment + Diagnoses + Recommendations to PostgreSQL
4. Returns structured AssessmentResponse to React
5. React navigates to ResultPage, renders explainable report
```
---
## Integration: Python ↔ SWI-Prolog
**Approach**: pyswip library (preferred), subprocess fallback
```python
# prolog_service.py pattern
from pyswip import Prolog
def run_diagnosis(symptoms: list[str]) -> dict:
    prolog = Prolog()
    prolog.consult("prolog/knowledge_base.pl")
    for s in symptoms:
        prolog.assertz(f"symptom({s})")
    results = list(prolog.query("possible(Condition), risk_level(Condition, Risk)"))
    return parse_results(results)
```
---
## Environment Variables (`.env`)
```
DATABASE_URL=postgresql+asyncpg://ohas_user:password@localhost:5432/ohas_db
SECRET_KEY=your-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
HUGGINGFACE_API_TOKEN=hf_xxxxxxxxxxxxx
HUGGINGFACE_MODEL_URL=https://api-inference.huggingface.co/models/...
```
---
## Ports
|
 Service    
|
 Port  
|
|
------------
|
-------
|
|
 React Dev  
|
 5173  
|
|
 FastAPI    
|
 8000  
|
|
 PostgreSQL 
|
 5432  
|

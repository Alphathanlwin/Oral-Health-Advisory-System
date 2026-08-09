# Build Plan — Oral Health Advisory System (OHAS)
## Development Approach
Build the system **backend-first, then frontend**, with the Prolog knowledge base designed upfront.
Each phase produces a working vertical slice of the system.
---
## Phase 1 — Project Setup & Auth
**Goal**: Running skeleton with working user registration and login.
### Backend
- [ ] Initialize FastAPI project structure (`backend/`)
- [ ] Set up `.env` and `config.py` with pydantic-settings
- [ ] Set up `database.py` with async SQLAlchemy engine
- [ ] Create `User` ORM model
- [ ] Set up Alembic and create initial migration (users table)
- [ ] Implement `auth_service.py`: register + login logic
- [ ] Implement `security.py`: bcrypt hashing + JWT encode/decode
- [ ] Create `auth.py` router: `POST /auth/register`, `POST /auth/login`
- [ ] Add `get_current_user` dependency
- [ ] Add CORS middleware
- [ ] Test endpoints via Swagger UI (`/docs`)
### Frontend
- [ ] Initialize Vite + React project (`frontend/`)
- [ ] Set up React Router v6 routes
- [ ] Create `AuthContext.jsx` with JWT storage in localStorage
- [ ] Build `LoginPage.jsx` with form + API call
- [ ] Build `RegisterPage.jsx` with form + API call
- [ ] Build `ProtectedRoute.jsx`
- [ ] Build `Navbar.jsx`
- [ ] Apply global CSS design system (colors, typography, dark theme)
---
## Phase 2 — Symptom Questionnaire
**Goal**: Users can complete the 4-step symptom questionnaire.
### Backend
- [ ] Create `Assessment`, `SymptomResponse` ORM models
- [ ] Create migration for assessments + symptom_responses tables
- [ ] Create `SymptomPayload` Pydantic schema
- [ ] Create `assessment.py` router: `POST /assessments/` (stub — saves symptoms only, returns dummy response)
### Frontend
- [ ] Build `NewAssessmentPage.jsx` with 4-step stepper
- [ ] Build `SymptomToggle.jsx` component (YES/NO toggle card)
- [ ] Build `SymptomForm.jsx` for each step
- [ ] Track step state + symptom responses in local state
- [ ] Add step navigation (Back / Next)
- [ ] Hook up final "Submit" to `POST /api/v1/assessments/`
---
## Phase 3 — Prolog Diagnosis Engine
**Goal**: Assessment submission triggers real Prolog reasoning and returns explainable results.
### Prolog
- [ ] Install SWI-Prolog locally
- [ ] Create `backend/prolog/knowledge_base.pl` (all 6 conditions from `prolog-kb.md`)
- [ ] Test `.pl` file manually via SWI-Prolog REPL
### Backend
- [ ] Install and configure `pyswip`
- [ ] Implement `prolog_service.py`: assert symptoms, query conditions + risk
- [ ] Create `Diagnosis`, `Recommendation` ORM models
- [ ] Create migration for diagnoses + recommendations tables
- [ ] Implement `assessment_service.py`: full orchestration (symptoms → Prolog → save to DB → return)
- [ ] Create `AssessmentResponse` Pydantic schema (with nested diagnoses + recommendations)
- [ ] Wire up `POST /assessments/` to full service
### Frontend
- [ ] Build `ResultPage.jsx`
- [ ] Build `RiskBadge.jsx`
- [ ] Build `DiagnosisCard.jsx` (condition + triggered rules as bullet points)
- [ ] Build `RecommendationCard.jsx` (action + urgency)
- [ ] Navigate to ResultPage after submission
---
## Phase 4 — Photo Upload & CV Integration
**Goal**: Optional mouth photo is processed by HuggingFace API and merged into symptom set.
### Backend
- [ ] Create `uploads/` directory + file saving logic in `image_utils.py`
- [ ] Implement image validation (type, size, resolution) in `image_utils.py`
- [ ] Implement `cv_service.py`: call HuggingFace Inference API
- [ ] Implement CV label → symptom key mapping
- [ ] Integrate CV results into `assessment_service.py` (merge before Prolog query)
- [ ] Handle `CV_SERVICE_UNAVAILABLE` gracefully (fallback to symptom-only)
### Frontend
- [ ] Build `PhotoUpload.jsx` component (drag-and-drop + preview)
- [ ] Add to Step 4 of questionnaire
- [ ] Send photo as base64 in assessment payload
---
## Phase 5 — History & Dashboard
**Goal**: Users can view past assessments and a summary dashboard.
### Backend
- [ ] Implement `GET /assessments/` with pagination
- [ ] Implement `GET /assessments/{id}` with ownership check
- [ ] Add eager loading for diagnoses + recommendations
### Frontend
- [ ] Build `HistoryPage.jsx` with paginated list
- [ ] Build `DashboardPage.jsx` with stats + recent assessments
- [ ] Make history rows clickable → navigate to ResultPage
---
## Phase 6 — Polish & Final Review
**Goal**: Clean, complete, and demo-ready system.
### Backend
- [ ] Add global exception handler for unhandled 500 errors
- [ ] Add input validation for all endpoints (Pydantic)
- [ ] Ensure all error codes match `api-standards.md`
- [ ] Write a `README.md` with setup + run instructions
### Frontend
- [ ] Add loading spinners to all async operations
- [ ] Add error toast notifications
- [ ] Ensure all forms have proper validation and error messages
- [ ] Add disclaimer text on ResultPage
- [ ] Final visual polish pass (spacing, animations, responsiveness)
### Testing & Documentation
- [ ] Manually test all 6 conditions with various symptom combinations
- [ ] Test photo upload (valid + invalid cases)
- [ ] Test history pagination
- [ ] Test JWT expiry and protected routes
- [ ] Write `progress-tracker.md` final status
---
## Phase Summary
|
 Phase 
|
 Focus                    
|
 Key Deliverable                             
|
|
-------
|
--------------------------
|
---------------------------------------------
|
|
 1     
|
 Setup + Auth             
|
 Working login/register + protected routes   
|
|
 2     
|
 Questionnaire            
|
 4-step symptom form → dummy response        
|
|
 3     
|
 Prolog Engine            
|
 Real diagnosis + explainable result page    
|
|
 4     
|
 CV Integration           
|
 Photo upload merged into diagnosis          
|
|
 5     
|
 History + Dashboard      
|
 Full assessment history visible             
|
|
 6     
|
 Polish + Docs            
|
 Demo-ready system with README               
|
# Progress Tracker — Oral Health Advisory System (OHAS)
> Update this file at the end of every development session.
> Mark items as `[x]` when complete, `[/]` when in progress, `[ ]` when pending.
---
## Phase 1 — Project Setup & Auth
### Backend
- [ ] FastAPI project structure initialized
- [ ] `.env` + `config.py` set up
- [ ] `database.py` with async SQLAlchemy
- [ ] `User` ORM model created
- [ ] Alembic initialized + initial migration run
- [ ] `auth_service.py` implemented (register + login)
- [ ] `security.py` implemented (bcrypt + JWT)
- [ ] `auth.py` router: `POST /auth/register`
- [ ] `auth.py` router: `POST /auth/login`
- [ ] `get_current_user` dependency implemented
- [ ] CORS middleware configured
- [ ] Auth endpoints tested via Swagger UI
### Frontend
- [ ] Vite + React project initialized
- [ ] React Router v6 routes configured
- [ ] `AuthContext.jsx` implemented
- [ ] `LoginPage.jsx` built and connected to API
- [ ] `RegisterPage.jsx` built and connected to API
- [ ] `ProtectedRoute.jsx` implemented
- [ ] `Navbar.jsx` built
- [ ] Global CSS design system applied (dark theme, colors, typography)
---
## Phase 2 — Symptom Questionnaire
### Backend
- [ ] `Assessment` ORM model created
- [ ] `SymptomResponse` ORM model created
- [ ] Migration for assessments + symptom_responses tables run
- [ ] `SymptomPayload` Pydantic schema created
- [ ] `POST /assessments/` stub endpoint implemented
### Frontend
- [ ] `NewAssessmentPage.jsx` with 4-step stepper built
- [ ] `SymptomToggle.jsx` component built
- [ ] Step 1 form (Pain & Sensitivity) built
- [ ] Step 2 form (Gum & Appearance) built
- [ ] Step 3 form (Mouth & Habits) built
- [ ] Step 4 form (Hygiene & Photo) built
- [ ] Step navigation (Back / Next) working
- [ ] Submit button wired to `POST /api/v1/assessments/`
---
## Phase 3 — Prolog Diagnosis Engine
### Prolog
- [ ] SWI-Prolog installed locally
- [ ] `knowledge_base.pl` created with all 6 conditions
- [ ] KB tested manually in SWI-Prolog REPL
### Backend
- [ ] `pyswip` installed and configured
- [ ] `prolog_service.py` implemented
- [ ] `Diagnosis` ORM model created
- [ ] `Recommendation` ORM model created
- [ ] Migration for diagnoses + recommendations tables run
- [ ] `assessment_service.py` fully implemented (Prolog orchestration)
- [ ] `AssessmentResponse` Pydantic schema created
- [ ] `POST /assessments/` wired to full service
### Frontend
- [ ] `ResultPage.jsx` built
- [ ] `RiskBadge.jsx` component built
- [ ] `DiagnosisCard.jsx` component built
- [ ] `RecommendationCard.jsx` component built
- [ ] Navigation to ResultPage after submission working
---
## Phase 4 — Photo Upload & CV Integration
### Backend
- [ ] `uploads/` directory structure created
- [ ] `image_utils.py` implemented (validation + save)
- [ ] `cv_service.py` implemented (HuggingFace API call)
- [ ] CV label → symptom key mapping implemented
- [ ] CV results integrated into `assessment_service.py`
- [ ] Graceful fallback on `CV_SERVICE_UNAVAILABLE`
### Frontend
- [ ] `PhotoUpload.jsx` component built
- [ ] Photo upload added to Step 4
- [ ] Base64 encoding of photo in payload working
---
## Phase 5 — History & Dashboard
### Backend
- [ ] `GET /assessments/` with pagination implemented
- [ ] `GET /assessments/{id}` with ownership check implemented
- [ ] Eager loading for diagnoses + recommendations added
### Frontend
- [ ] `HistoryPage.jsx` built with paginated list
- [ ] `DashboardPage.jsx` built (stats + recent assessments)
- [ ] History rows clickable → navigate to ResultPage
---
## Phase 6 — Polish & Final Review
### Backend
- [ ] Global exception handler added
- [ ] Input validation confirmed for all endpoints
- [ ] All error codes match `api-standards.md`
- [ ] `README.md` written
### Frontend
- [ ] Loading spinners added to all async operations
- [ ] Error toast notifications implemented
- [ ] All form validations complete
- [ ] Disclaimer text on ResultPage added
- [ ] Final visual polish done (spacing, animations, responsiveness)
### Testing & Documentation
- [ ] All 6 conditions tested manually (symptom combinations)
- [ ] Photo upload tested (valid + invalid cases)
- [ ] History pagination tested
- [ ] JWT expiry + protected route tested
- [ ] Final `progress-tracker.md` status updated
---
## Notes / Decisions Log
> Record important decisions made during development here.
|
 Date 
|
 Decision 
|
 Reason 
|
|
------
|
----------
|
--------
|
|
|
|
|

# Progress Tracker — Oral Health Advisory System (OHAS)
> Update this file at the end of every development session.
> Mark items as `[x]` when complete, `[/]` when in progress, `[ ]` when pending.
---
## Phase 1 — Project Setup & Auth
### Backend
- [x] FastAPI project structure initialized
- [x] `.env` + `config.py` set up
- [x] `database.py` with async SQLAlchemy
- [x] `User` ORM model created
- [x] Alembic initialized + initial migration run
- [x] `auth_service.py` implemented (register + login)
- [x] `security.py` implemented (bcrypt + JWT)
- [x] `auth.py` router: `POST /auth/register`
- [x] `auth.py` router: `POST /auth/login`
- [x] `get_current_user` dependency implemented
- [x] CORS middleware configured
- [x] Auth endpoints tested via Swagger UI
### Frontend
- [x] Vite + React project initialized
- [x] React Router routes configured (using v7, not v6 as originally planned)
- [x] `AuthContext.jsx` implemented
- [x] `LoginPage.jsx` built and connected to API
- [x] `RegisterPage.jsx` built and connected to API
- [x] `ProtectedRoute.jsx` implemented
- [x] `Navbar.jsx` built
- [x] Global CSS design system applied (dark theme, colors, typography)
---
## Phase 2 — Symptom Questionnaire
### Backend
- [x] `Assessment` ORM model created
- [x] `SymptomResponse` ORM model created
- [x] Migration for assessments + symptom_responses tables run
- [x] `SymptomPayload` Pydantic schema created
- [x] `POST /assessments/` stub endpoint implemented (saves symptoms, returns dummy `risk_level: LOW`)
### Frontend
- [x] `NewAssessmentPage.jsx` with 4-step stepper built
- [x] `SymptomToggle.jsx` component built
- [x] Step 1 form (Pain & Sensitivity) built
- [x] Step 2 form (Gum & Appearance) built
- [x] Step 3 form (Mouth & Habits) built
- [x] Step 4 form (Hygiene & Photo) built — photo upload added (`PhotoUpload.jsx`)
- [x] Step navigation (Back / Next) working
- [x] Submit button wired to `POST /api/v1/assessments/`
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
- [x] `RiskBadge.jsx` component built
- [ ] `DiagnosisCard.jsx` component built
- [ ] `RecommendationCard.jsx` component built
- [ ] Navigation to ResultPage after submission working
---
## Phase 4 — Photo Upload & CV Integration
### Backend
- [x] `uploads/` directory structure created
- [x] `image_utils.py` implemented (validation + save)
- [x] `cv_service.py` implemented (HuggingFace API call)
- [x] CV label → symptom key mapping implemented
- [x] CV results integrated into `assessment_service.py`
- [x] Graceful fallback on `CV_SERVICE_UNAVAILABLE`
### Frontend
- [x] `PhotoUpload.jsx` component built
- [x] Photo upload added to Step 4
- [x] Base64 encoding of photo in payload working
---
## Phase 5 — History & Dashboard
### Backend
- [ ] `GET /assessments/` with pagination implemented
- [ ] `GET /assessments/{id}` with ownership check implemented
- [ ] Eager loading for diagnoses + recommendations added
### Frontend
- [ ] `HistoryPage.jsx` built with paginated list
- [x] `DashboardPage.jsx` built (stats + recent assessments)
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
| Date | Decision | Reason |
|------|----------|--------|
| 2026-08-09 | Direct Supabase DB host (`db.*.supabase.co`) is IPv6-only and unreachable from this machine; switched to **transaction pooler** (`aws-0-ap-northeast-1.pooler.supabase.com:6543`) with `?ssl=require`. | Pooler resolves to IPv4 and allows SSL; direct host has only an AAAA record and no IPv6 route. |
| 2026-08-09 | Disabled asyncpg statement caching (`statement_cache_size=0`, `prepared_statement_cache_size=0`) in `database.py` and `alembic/env.py`. | Supabase transaction pooler does not support asyncpg prepared statements (`DuplicatePreparedStatementError`). |
| 2026-08-09 | Pinned `bcrypt==4.0.1` in `requirements.txt`. | `passlib 1.7.4` is incompatible with `bcrypt>=4.1` (removed `__about__`), crashing register with 500. |
| 2026-08-11 | `PhotoUpload.jsx` emits the full `data:` URI to the page; `NewAssessmentPage.jsx` strips the prefix and sends raw base64 as `photo_base64`. | Backend `decode_base64_image` also accepts the `data:` URI, but raw base64 keeps the payload minimal. |
| 2026-08-11 | Ran the previously-pending `c243bf08b89a_create_assessments_and_symptom_` migration against the live Supabase DB (`alembic upgrade head`). | The DB was unreachable in the session that wrote the migration; this session's `.env` reaches it fine, and applying it was required to test the CV/photo work end-to-end. User confirmed before running. |
| 2026-08-11 | `CVServiceUnavailableError` (plain `Exception`, not `HTTPException`) is caught inside `assessment_service.create()` and never surfaces to the client — `image_analysis_result` is set to `{"status": "CV_SERVICE_UNAVAILABLE"}` and the assessment still saves with symptom-only data. | Photo is optional; a CV outage must not fail assessment submission (Phase 4 requirement: "Handle CV_SERVICE_UNAVAILABLE gracefully"). Verified live: real HF call fails against the placeholder `.env` token and the fallback path saves correctly (HTTP 201). |

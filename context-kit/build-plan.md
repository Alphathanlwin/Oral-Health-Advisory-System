# Build Plan — Oral Health Advisory System (OHAS)
## Development Approach
Build the system **backend-first, then frontend**, with the Prolog knowledge base designed upfront.
Each phase produces a working vertical slice of the system.
---
## Phase 1 — Project Setup & Auth
**Goal**: Running skeleton with working user registration and login.
### Backend
- [x] Initialize FastAPI project structure (`backend/`)
- [x] Set up `.env` and `config.py` with pydantic-settings
- [x] Set up `database.py` with async SQLAlchemy engine
- [x] Create `User` ORM model
- [x] Set up Alembic and create initial migration (users table)
- [x] Implement `auth_service.py`: register + login logic
- [x] Implement `security.py`: bcrypt hashing + JWT encode/decode
- [x] Create `auth.py` router: `POST /auth/register`, `POST /auth/login`
- [x] Add `get_current_user` dependency
- [x] Add CORS middleware
- [x] Test endpoints via Swagger UI (`/docs`)
### Frontend
- [x] Initialize Vite + React project (`frontend/`)
- [x] Set up React Router v6 routes (using v7, not v6 as originally planned)
- [x] Create `AuthContext.jsx` with JWT storage in localStorage
- [x] Build `LoginPage.jsx` with form + API call
- [x] Build `RegisterPage.jsx` with form + API call
- [x] Build `ProtectedRoute.jsx`
- [x] Build `Navbar.jsx`
- [x] Apply global CSS design system (colors, typography, dark theme)
---
## Phase 2 — Symptom Questionnaire
**Goal**: Users can complete the 4-step symptom questionnaire.
### Backend
- [x] Create `Assessment`, `SymptomResponse` ORM models
- [x] Create migration for assessments + symptom_responses tables
- [x] Create `SymptomPayload` Pydantic schema
- [x] Create `assessment.py` router: `POST /assessments/` (superseded by Phase 3 — wired to the full Prolog-backed service, not just a stub)
### Frontend
- [x] Build `NewAssessmentPage.jsx` with 4-step stepper
- [x] Build `SymptomToggle.jsx` component (YES/NO toggle card)
- [x] Build `SymptomForm.jsx` for each step
- [x] Track step state + symptom responses in local state
- [x] Add step navigation (Back / Next)
- [x] Hook up final "Submit" to `POST /api/v1/assessments/`
---
## Phase 3 — Prolog Diagnosis Engine
**Goal**: Assessment submission triggers real Prolog reasoning and returns explainable results.
### Prolog
- [x] Install SWI-Prolog locally
- [x] Create `backend/prolog/knowledge_base.pl` (all 6 conditions from `prolog-kb.md`)
- [x] Test `.pl` file manually via SWI-Prolog REPL
### Backend
- [x] Implement `prolog_service.py`: assert symptoms, query conditions + risk (via a **subprocess** bridge to the `swipl` CLI, not `pyswip` — its embedded engine isn't request-isolated for concurrent async requests; see progress-tracker.md decision log)
- [x] Create `Diagnosis`, `Recommendation` ORM models
- [x] Create migration for diagnoses + recommendations tables
- [x] Implement `assessment_service.py`: full orchestration (symptoms → Prolog → save to DB → return)
- [x] Create `AssessmentResponse` Pydantic schema (with nested diagnoses + recommendations)
- [x] Wire up `POST /assessments/` to full service
### Frontend
- [x] Build `ResultPage.jsx`
- [x] Build `RiskBadge.jsx`
- [x] Build `DiagnosisCard.jsx` (condition + triggered rules as bullet points)
- [x] Build `RecommendationCard.jsx` (action + urgency)
- [x] Navigate to ResultPage after submission
---
## Phase 3A — Live AI Screening: Foundation (Frontend-only)
**Goal**: Prove out the "Dr. Ava" avatar + guided-session pacing before touching camera or backend. This is a new, parallel entry point alongside the static questionnaire (Phase 2) — it does not block or replace it.
### Frontend
- [ ] Build `AiGuide.jsx` — avatar component, `state` prop, pose swapping (idle / look here / great job / processing / here's what I found), idle "breathing" animation, speech-bubble caption
- [ ] Build `utils/speech.js` — `speak(text, { onStart, onEnd })` wrapper around Web Speech API `SpeechSynthesis`
- [ ] Implement mouth-swap talking animation (`useTalkingMouth` hook, ~140ms frame cycle) driven by `onStart` / `onEnd`
- [ ] Build `LiveScreeningPage.jsx` with state machine: `intro → ask_symptoms → capture_front → capture_upper → capture_lower → analyzing → reveal` (dummy/hardcoded transitions first, no real camera or API calls)
- [ ] Add route `/assessment/live` in `App.jsx`
- [ ] Add "Live AI Screening" button on `DashboardPage.jsx` (alongside existing "Start New Assessment")
- [ ] Match Pencil.dev screen designs for each state's layout
**Deliverable**: Full click-through of the guided flow with Dr. Ava talking/animating; capture and analysis are still faked.
---
## Phase 3B — Live AI Screening: Symptom Voice Step
**Goal**: The `ask_symptoms` state collects real, usable data.
### Frontend
- [ ] Build `SymptomVoiceStep.jsx` — one YES/NO question at a time, reusing existing symptom key list and `SymptomToggle` styling
- [ ] Wire answers into local state matching the existing `symptoms{}` payload shape
- [ ] Dr. Ava speaks each question via `speak()` before showing the Yes/No buttons
- [ ] Progress dots reflect question count
**Deliverable**: Symptom-collection portion is fully functional and produces the same data shape as the static form.
---
## Phase 3C — Live AI Screening: Guided Camera Capture
**Goal**: Real multi-angle photo capture with on-screen guidance.
### Frontend
- [ ] Build `GuidedCapture.jsx` — `navigator.mediaDevices.getUserMedia`, live `<video>` preview, capture via `<canvas>`
- [ ] Build 3 SVG overlay guides (front bite / upper arch / lower arch) matching Pencil.dev designs
- [ ] Sequential flow: capture → confirm/retake → next angle
- [ ] Camera-denied fallback: Dr. Ava apologetic pose → falls back to `PhotoUpload.jsx`
- [ ] Store 3 captured images as base64 in local state
**Deliverable**: Front end produces real `symptoms{}` + real `photos: {front, upper, lower}`, ready to submit.
---
## Phase 3D — Live AI Screening: Backend Multi-Photo + CV Integration
**Goal**: Backend can receive and process what Phase 3C produces. (This folds in the original Phase 4 CV work, pulled forward.)
### Backend
- [ ] Update `AssessmentCreate` schema: `photo_base64` → `photos: {front, upper, lower}` (all optional, nullable)
- [ ] Create `uploads/` directory + file saving logic in `image_utils.py`
- [ ] Implement image validation (type, size, resolution) in `image_utils.py`
- [ ] Implement `cv_service.py`: call HuggingFace Inference API per image
- [ ] Implement CV label → symptom key mapping
- [ ] Merge (union) CV-detected symptoms across all 3 images before the Prolog query
- [ ] Integrate into `assessment_service.py` (merge CV symptoms with questionnaire symptoms)
- [ ] Handle `CV_SERVICE_UNAVAILABLE` gracefully (fallback to symptom-only diagnosis)
- [ ] Confirm `prolog_service.py` + `knowledge_base.pl` (Phase 3) are in place
**Deliverable**: The `analyzing` state calls the real `POST /assessments/` endpoint and receives a real diagnosis.
---
## Phase 3E — Live AI Screening: Reveal + Result Integration
**Goal**: Close the loop from Live Screening into the existing results system.
### Frontend
- [ ] `reveal` state shows risk-level badge + short spoken summary via Dr. Ava
- [ ] Navigate to `ResultPage.jsx` with the real assessment ID
- [ ] Add Dr. Ava "here's what I found" treatment to `ResultPage.jsx` next to `RiskBadge` (reuses `AiGuide.jsx`)
- [ ] Confirm `DiagnosisCard.jsx` / `RecommendationCard.jsx` render correctly for Live-Screening-originated assessments
**Deliverable**: Live Screening is a fully working alternate entry point into the existing assessment → result pipeline.
---
## Phase 4 — AI Chatbot (Intake + Explainer)
**Goal**: Add constrained, non-diagnostic LLM assistance around the existing Prolog pipeline — Prolog remains the sole diagnostic authority; the LLM never generates a diagnosis.
### Backend
- [ ] Implement `llm_service.py` — thin wrapper around chosen LLM API
- [ ] Implement `chat_intake_service.py`: free-text → extracted `symptoms{}` keys, validated against `database-schema.md` allowed keys
- [ ] Add `routers/chat.py`: `POST /api/v1/chat/intake`
- [ ] Implement `chat_explain_service.py`: post-result Q&A grounded strictly in that assessment's own `triggered_rules` / `explanation` / `recommendation`; refuses anything outside that data
- [ ] Add `POST /api/v1/chat/explain`
- [ ] Create `schemas/chat.py`: `ChatIntakeRequest/Response`, `ChatExplainRequest/Response`
- [ ] Add `LLM_API_KEY`, `LLM_MODEL` to `.env`
- [ ] Handle `LLM_SERVICE_UNAVAILABLE` (503) gracefully
### Frontend
- [ ] Optional free-text entry point in the symptom step (Live Screening and/or static form), parsed via `/chat/intake`
- [ ] Chat input component on `ResultPage.jsx`, wired to `/chat/explain`
- [ ] Dr. Ava optionally speaks the explainer answer via `speak()`
---
## Phase 5 — Delivery & Discovery
**Goal**: Report delivery via Telegram, plus real nearby clinic discovery (Google Places).
### Backend
- [ ] Add `telegram_chat_id` column to `users`
- [ ] Implement bot-linking flow (`/start` deep link)
- [ ] Implement `notification_service.py` — Telegram Bot API `sendMessage` after assessment save (fire-and-forget, try/except, never blocks response)
- [ ] Implement `clinic_service.py` — Google Places Nearby Search (`type=dentist`)
- [ ] Add `GET /api/v1/clinics/nearby?lat=&lng=&radius=`
- [ ] Handle `CLINIC_SERVICE_UNAVAILABLE` (503) gracefully
- [ ] Add `GOOGLE_PLACES_API_KEY` to `.env`
### Frontend
- [ ] "Find nearby clinics" button + list UI on `ResultPage.jsx` (name, address, rating, distance, phone)
- [ ] Telegram account linking UI (settings or dashboard)
**Note**: Real calendar/slot booking (Google Calendar API) is explicitly parked — this phase is clinic discovery only, no booking.
---
## Phase 6 — History & Dashboard
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
## Phase 7 — Polish & Final Review
**Goal**: Clean, complete, and demo-ready system covering both the static-form and Live-Screening paths.
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
- [ ] Final visual polish pass (spacing, animations, responsiveness) across both entry points
### Testing & Documentation
- [ ] Manually test all 6 conditions with various symptom combinations
- [ ] Test photo upload (valid + invalid cases) — static form AND Live Screening
- [ ] Test Live Screening camera fallback path
- [ ] Test chatbot intake + explainer grounding (no off-topic answers)
- [ ] Test Telegram delivery + nearby clinic discovery
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
 3A    
|
 Live Screening: Foundation
|
 Dr. Ava avatar + guided flow (dummy data)   
|
|
 3B    
|
 Live Screening: Symptom Voice
|
 Real symptom capture via guided Q&A         
|
|
 3C    
|
 Live Screening: Guided Capture
|
 Real multi-angle camera capture             
|
|
 3D    
|
 Live Screening: CV Backend
|
 Photos merged into diagnosis via Prolog     
|
|
 3E    
|
 Live Screening: Reveal
|
 Live Screening feeds into existing ResultPage
|
|
 4     
|
 AI Chatbot             
|
 Constrained intake + explainer chat         
|
|
 5     
|
 Delivery + Discovery      
|
 Telegram report delivery + nearby clinics   
|
|
 6     
|
 History + Dashboard      
|
 Full assessment history visible             
|
|
 7     
|
 Polish + Docs            
|
 Demo-ready system with README               
|
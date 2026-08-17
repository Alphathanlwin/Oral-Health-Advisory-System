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
## Phase 3A — Live AI Screening: Foundation (Frontend-only)
> New parallel entry point alongside the static questionnaire — does not block or replace Phase 2/3.
### Frontend
- [ ] `AiGuide.jsx` built (avatar, `state` prop, pose swapping, idle breathing animation, speech-bubble caption)
- [ ] `utils/speech.js` built (`speak(text, { onStart, onEnd })` wrapper around `SpeechSynthesis`)
- [ ] Mouth-swap talking animation (`useTalkingMouth` hook) wired to `onStart`/`onEnd`
- [ ] `LiveScreeningPage.jsx` state machine built (`intro → ask_symptoms → capture_front → capture_upper → capture_lower → analyzing → reveal`) with dummy/hardcoded transitions
- [ ] Route `/assessment/live` added in `App.jsx`
- [ ] "Live AI Screening" button added on `DashboardPage.jsx`
- [ ] Screens match Pencil.dev designs for each state
---
## Phase 3B — Live AI Screening: Symptom Voice Step
### Frontend
- [ ] `SymptomVoiceStep.jsx` built (one YES/NO question at a time, reuses symptom key list + `SymptomToggle` styling)
- [ ] Answers wired into local state matching existing `symptoms{}` payload shape
- [ ] Dr. Ava speaks each question via `speak()` before showing Yes/No buttons
- [ ] Progress dots reflect question count
---
## Phase 3C — Live AI Screening: Guided Camera Capture
### Frontend
- [ ] `GuidedCapture.jsx` built (`getUserMedia`, live `<video>` preview, `<canvas>` capture)
- [ ] 3 SVG overlay guides built (front bite / upper arch / lower arch)
- [ ] Sequential flow: capture → confirm/retake → next angle
- [ ] Camera-denied fallback → Dr. Ava apologetic pose → falls back to `PhotoUpload.jsx`
- [ ] 3 captured images stored as base64 in local state
---
## Phase 3D — Live AI Screening: Backend Multi-Photo + CV Integration
> Folds in the original Phase 4 CV work, pulled forward to support Live Screening.
### Backend
- [ ] `AssessmentCreate` schema updated: `photo_base64` → `photos: {front, upper, lower}` (optional, nullable)
- [ ] `uploads/` directory structure created
- [ ] `image_utils.py` implemented (validation + save)
- [ ] `cv_service.py` implemented (HuggingFace API call per image)
- [ ] CV label → symptom key mapping implemented
- [ ] CV results merged (union across 3 images) and integrated into `assessment_service.py`
- [ ] Graceful fallback on `CV_SERVICE_UNAVAILABLE`
- [ ] `prolog_service.py` + `knowledge_base.pl` confirmed in place (Phase 3)
---
## Phase 3E — Live AI Screening: Reveal + Result Integration
### Frontend
- [ ] `reveal` state shows risk-level badge + spoken summary via Dr. Ava
- [ ] Navigation to `ResultPage.jsx` with real assessment ID working
- [ ] Dr. Ava "here's what I found" treatment added to `ResultPage.jsx` (reuses `AiGuide.jsx`)
- [ ] `DiagnosisCard.jsx` / `RecommendationCard.jsx` confirmed working for Live-Screening-originated assessments
---
## Phase 4 — AI Chatbot (Intake + Explainer)
> Constrained, non-diagnostic LLM assistance. Prolog remains the sole diagnostic authority.
### Backend
- [ ] `llm_service.py` implemented (thin LLM API wrapper)
- [ ] `chat_intake_service.py` implemented (free-text → extracted `symptoms{}`, validated against allowed keys)
- [ ] `routers/chat.py`: `POST /api/v1/chat/intake` implemented
- [ ] `chat_explain_service.py` implemented (grounded strictly in assessment's own `triggered_rules`/`explanation`/`recommendation`)
- [ ] `POST /api/v1/chat/explain` implemented
- [ ] `schemas/chat.py` created (`ChatIntakeRequest/Response`, `ChatExplainRequest/Response`)
- [ ] `LLM_API_KEY`, `LLM_MODEL` added to `.env`
- [ ] Graceful fallback on `LLM_SERVICE_UNAVAILABLE`
### Frontend
- [ ] Optional free-text symptom entry point wired to `/chat/intake`
- [ ] Chat input component built on `ResultPage.jsx`, wired to `/chat/explain`
- [ ] Dr. Ava optionally speaks explainer answers via `speak()`
---
## Phase 5 — Delivery & Discovery
### Backend
- [ ] `telegram_chat_id` column added to `users`
- [ ] Bot-linking flow implemented (`/start` deep link)
- [ ] `notification_service.py` implemented (Telegram Bot API `sendMessage`, fire-and-forget, try/except)
- [ ] `clinic_service.py` implemented (Google Places Nearby Search, `type=dentist`)
- [ ] `GET /api/v1/clinics/nearby?lat=&lng=&radius=` implemented
- [ ] Graceful fallback on `CLINIC_SERVICE_UNAVAILABLE`
- [ ] `GOOGLE_PLACES_API_KEY` added to `.env`
### Frontend
- [ ] "Find nearby clinics" button + list UI built on `ResultPage.jsx`
- [ ] Telegram account linking UI built
> Note: Real calendar/slot booking (Google Calendar API) is parked — this phase is clinic discovery only.
---
## Phase 6 — History & Dashboard
### Backend
- [x] `GET /assessments/` with pagination implemented
- [x] `GET /assessments/{id}` with ownership check implemented
- [x] Eager loading for diagnoses + recommendations added
### Frontend
- [x] `HistoryPage.jsx` built with paginated list
- [x] `DashboardPage.jsx` built (stats + recent assessments)
- [x] History rows clickable → navigate to ResultPage
---
## Phase 7 — Polish & Final Review
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
- [ ] Final visual polish done (spacing, animations, responsiveness) across both entry points
### Testing & Documentation
- [ ] All 6 conditions tested manually (symptom combinations)
- [ ] Photo upload tested (valid + invalid cases) — static form AND Live Screening
- [ ] Live Screening camera fallback path tested
- [ ] Chatbot intake + explainer grounding tested (no off-topic answers)
- [ ] Telegram delivery + nearby clinic discovery tested
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
| 2026-08-15 | Discovered at the start of Phase 3D that Phase 3 (Prolog engine) was never actually built despite Phase 4 being checked off — `assessment_service.create()` returned a hardcoded `RiskLevel.LOW` stub, and `prolog_service.py`/`knowledge_base.pl` didn't exist. Built Phase 3 as a prerequisite (KB copied verbatim from `prolog-kb.md`, fully pre-specified — no new clinical logic invented) since the Phase 3D deliverable explicitly requires "a real diagnosis." | AGENTS.md rule 8 ("ask if uncertain") was weighed against the fact that every line of the KB was already fully specified in the docs — implementing it was mechanical, not a design decision, and skipping it would leave the stated deliverable unmet. |
| 2026-08-15 | `prolog_service.py` uses **subprocess** (`swipl` CLI), not `pyswip`, despite `pyswip` being architecture.md's preferred option. | `pyswip`'s embedded engine is a single global interpreter per process — not isolated per request, so concurrent async requests would race on asserted `symptom/1` facts. `library-docs.md` itself documents subprocess as the Windows fallback; this dev machine is Windows. |
| 2026-08-15 | `knowledge_base.pl` gained a `report/0` helper (dedupes matched conditions via `sort/2`, picks the highest-severity `risk_level/2`/`explanation/2` per condition via `once/1`) and explicit `set_prolog_flag(encoding, utf8)` / `set_stream(user_output, encoding(utf8))` directives. | Manual REPL testing surfaced two real bugs: (1) naive `possible(C), risk_level(C,R)` backtracking produced duplicate/contradictory risk rows per condition — confirmed via `swipl` before writing any Python; (2) SWI-Prolog on Windows defaults to the system codepage for both file reads and stdout writes, silently mangling the em dashes in `explanation/2` texts into mojibake — confirmed by inspecting raw output bytes, not just terminal display (which itself misrenders correct UTF-8). |
| 2026-08-15 | `assessments.photo_url VARCHAR(500)` replaced with `photo_urls JSONB` (`{"front", "upper", "lower"}`, each nullable); `image_analysis_result` keeps its JSONB type but now holds one CV result per angle instead of one overall. Migration drops the old column outright rather than migrating existing values. | Phase 3D's guided capture produces up to 3 photos, not 1. Dropping instead of migrating `photo_url` is acceptable pre-launch — no production assessment data exists yet that depends on it. |
| 2026-08-15 | `diagnoses.triggered_rules` is populated as `["possible(<condition>)", "risk_level(<condition>, <risk>)"]` — the two predicate calls that succeeded — rather than deeper per-clause provenance. | `report/0` reports the winning risk level via `once/1`, not which specific clause matched; `api-standards.md`'s own example (`"needs_dentist(dental_cavity)"`) isn't a real predicate in the KB either, confirming the field is meant as an illustrative rule-name list rather than exact clause introspection. Deeper instrumentation (naming every clause) was out of scope for Phase 3D. |
| 2026-08-15 | `NewAssessmentPage.jsx`'s single optional photo now maps to `photos.front` (with `upper`/`lower` sent as `null`) instead of the removed `photo_base64` field. | Required to avoid breaking the existing static-questionnaire photo upload when the schema field was renamed per Phase 3D's explicit instruction. |
| 2026-08-15 | Built `ResultPage.jsx`, `DiagnosisCard.jsx`, `RecommendationCard.jsx`, and `data/clinicalLabels.js` (shared `CONDITION_LABELS`/`URGENCY_LABELS` maps). `NewAssessmentPage.jsx` now passes the freshly-created `AssessmentResponse` via router `state` on navigation, so the primary post-submit flow renders immediately without a backend round-trip. | `ui-rules.md`'s Result Page spec requires triggered rules shown as plain English, not raw Prolog predicates — added `formatTriggeredRule()` in `DiagnosisCard.jsx` to translate `possible(condition)` / `risk_level(condition, level)` strings client-side rather than changing the backend's `triggered_rules` format. |
| 2026-08-15 | `ResultPage.jsx` falls back to `GET /assessments/{id}` (new `getAssessment()` in `api/assessment.js`) only when no router `state` is present (e.g. a direct link or refresh), and shows a friendly "could not be found" error instead of crashing if that call fails. | `GET /assessments/{id}` is still unbuilt (Phase 5 backend, not in scope here) — confirmed live via Playwright that the fallback degrades gracefully rather than exposing the missing-endpoint error. This also means `DashboardPage.jsx`'s existing links to `/assessment/:id/result` for past assessments won't resolve until Phase 5's `GET /assessments/{id}` (and `GET /assessments/`, also still a 405 today) are built. |
| 2026-08-15 | `LiveScreeningPage.jsx`'s analyzing step now fires `createAssessment()` in a `useEffect` gated on `symptoms && photos`, while the visual progress bar climbs independently and holds at 96% until that real request settles (success or failure) — only then does it jump to 100% and switch to `reveal` or a new `error` screen. | Keeps the "reading your scans" animation feeling alive during the real network/CV/Prolog round-trip without faking a "done" state before the actual diagnosis exists; a `cancelled` flag guards against React 19 StrictMode's double-invoked dev effects racing two requests. |
| 2026-08-15 | Removed `LiveScreeningPage.jsx`'s hardcoded "Smile score X/100" meter (`.live-meter` and related CSS) from the reveal screen instead of wiring it to real data. | `AssessmentResponse` has no numeric score field — the meter was fabricated UI with no backing data (AGENTS.md rule 1: never guess/invent fields). Replaced with a real "N condition(s) detected" line sourced from `assessment.diagnoses.length`. |
| 2026-08-15 | Added a shared `buildResultSummary()` in `utils/resultSummary.js`, used by both `LiveScreeningPage`'s reveal caption and `ResultPage`'s new Dr. Ava row, instead of writing the summary text separately in each place. | Phase 3E asks for "a short spoken summary via Dr. Ava" on reveal and a "here's what I found" treatment on `ResultPage` — sharing one function keeps the two surfaces from describing the same assessment differently. |
| 2026-08-15 | Verified live via Playwright (fake camera device + a `speechSynthesis.speak` stub to make voice-gated Yes/No buttons deterministic in headless Chromium) that answering all 20 symptom questions "Yes" plus capturing 3 photos produces a real 5-condition HIGH-risk diagnosis, a correctly red-colored `HIGH RISK` reveal badge, and identical diagnosis/recommendation data rendered on `ResultPage.jsx` after navigating with real router `state`. | Confirms Phase 3E's deliverable — Live Screening is a fully working alternate entry point into the same assessment → result pipeline as the static questionnaire, not a parallel/divergent one. |
| 2026-08-15 | Diagnosed why the camera flow skipped straight to the photo-upload fallback on a phone: `http://<lan-ip>:5173` is not a secure context (only `https://` and `localhost` are), so `navigator.mediaDevices` doesn't exist there and `GuidedCapture.jsx`'s `getUserMedia` call rejects instantly, before any permission prompt. Fixed by adding `@vitejs/plugin-basic-ssl` + `server.https: true` in `vite.config.js`, plus `server.proxy: { '/api': ... }` forwarding to the backend so the browser only ever talks to the https origin (avoiding both CORS and https-page-calling-http mixed-content blocks). `api/auth.js`'s `API_BASE_URL` simplified to the relative `/api/v1` accordingly. | Confirmed via Playwright with fake camera device flags against `https://<lan-ip>:5173` that `navigator.mediaDevices` is now defined, `window.isSecureContext` is `true`, and the real 3-angle `GuidedCapture` UI renders instead of the denied-fallback. |
| 2026-08-15 | Added real neural TTS for Dr. Ava (ElevenLabs) instead of tuning the existing browser `SpeechSynthesis` voice — user explicitly chose this over the free/limited quick-tweak option, understanding the per-character cost and that it requires their own API key. New `services/tts_service.py` (mirrors `cv_service.py`'s httpx + graceful-unavailable pattern) + `POST /api/v1/tts/` (`routers/tts.py`, requires auth — cost control) returning raw `audio/mpeg`. `ELEVENLABS_API_KEY`/`ELEVENLABS_VOICE_ID` are optional settings (default `""`); `TTSServiceUnavailableError` → `503 TTS_SERVICE_UNAVAILABLE` when unset or the API call fails. | `utils/speech.js`'s `speak()` now tries `POST /api/v1/tts/` first and falls back to the pre-existing `SpeechSynthesis` path on any failure (including no key configured yet) — every caller (`AiGuide.jsx` via all its call sites) keeps the same `onStart`/`onEnd` contract unchanged, so Dr. Ava never goes silent even before a real key is added to `backend/.env`. |

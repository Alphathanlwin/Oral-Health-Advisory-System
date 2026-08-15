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
- [x] SWI-Prolog installed locally (10.0.2, on PATH)
- [x] `knowledge_base.pl` created with all 6 conditions
- [x] KB tested manually in SWI-Prolog REPL (single-condition, multi-condition, and no-symptom cases)
### Backend
- [x] `prolog_service.py` implemented — **subprocess-based** (pyswip skipped: not request-isolated for concurrent async requests, and flaky on Windows per `library-docs.md`'s own caveat)
- [x] `Diagnosis` ORM model created
- [x] `Recommendation` ORM model created
- [x] Migration for diagnoses + recommendations tables run
- [x] `assessment_service.py` fully implemented (Prolog orchestration)
- [x] `AssessmentResponse` Pydantic schema created (nested `diagnoses[].recommendations[]`)
- [x] `POST /assessments/` wired to full service
### Frontend
- [x] `ResultPage.jsx` built
- [x] `RiskBadge.jsx` component built
- [x] `DiagnosisCard.jsx` component built
- [x] `RecommendationCard.jsx` component built
- [x] Navigation to ResultPage after submission working
- [x] **Phase 3E**: `LiveScreeningPage.jsx`'s analyzing step calls the real `POST /assessments/`; reveal step shows the real risk badge + a Dr. Ava spoken summary; "View full results" navigates to `ResultPage.jsx` with the real assessment ID + data. `ResultPage.jsx` gained a Dr. Ava "here's what I found" treatment (reused `AiGuide.jsx`) next to the risk badge, driven by a summary shared with the reveal step (`utils/resultSummary.js`).
---
## Phase 4 — Photo Upload & CV Integration
### Backend
- [x] `uploads/` directory structure created
- [x] `image_utils.py` implemented (validation + save) — reused as-is per-photo for Phase 3D, no changes needed
- [x] `cv_service.py` implemented (HuggingFace API call)
- [x] CV label → symptom key mapping implemented
- [x] CV results integrated into `assessment_service.py`
- [x] Graceful fallback on `CV_SERVICE_UNAVAILABLE`
- [x] **Phase 3D**: upgraded from single photo to `photos: {front, upper, lower}` — CV runs per-image, detected symptoms unioned across all 3 before the Prolog query; a per-image `CV_SERVICE_UNAVAILABLE` no longer drops the other images' results
### Frontend
- [x] `PhotoUpload.jsx` component built
- [x] Photo upload added to Step 4
- [x] Base64 encoding of photo in payload working — updated to send `photos: {front, upper: null, lower: null}` after the Phase 3D schema rename
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

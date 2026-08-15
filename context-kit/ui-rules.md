UI Rules — Oral Health Advisory System (OHAS)
Design System
Color Palette
css

/* Primary — medical teal */
--color-primary:     #0ea5e9;  /* sky-500 */
--color-primary-dark:#0284c7;  /* sky-600 */
/* Risk Level Colors */
--color-risk-low:    #22c55e;  /* green-500 */
--color-risk-medium: #f59e0b;  /* amber-500 */
--color-risk-high:   #ef4444;  /* red-500 */
/* Backgrounds */
--color-bg:          #0f172a;  /* slate-900 — dark mode */
--color-surface:     #1e293b;  /* slate-800 */
--color-border:      #334155;  /* slate-700 */
/* Text */
--color-text:        #f1f5f9;  /* slate-100 */
--color-muted:       #94a3b8;  /* slate-400 */
Typography
Import from Google Fonts: Inter (body) + Outfit (headings)
Base font size: 16px
Use rem units for spacing and font sizes
Page Structure
1. Login / Register Pages
Centered card layout, max-width 420px
OHAS logo / name at top
Form fields: email, password (+ full_name, dob for register)
Submit button spans full width
Link to switch between login ↔ register
Show error messages inline below affected field
2. Dashboard Page (protected)
Navbar at top with logo + user name + logout button
Hero section: welcome message + "Start New Assessment" CTA button
Summary stats row: Total Assessments | Last Risk Level | Last Assessment Date
Recent assessments list (last 3, with link to full history)
3. New Assessment Page (multi-step, protected)
The questionnaire is broken into 4 steps:

Step	Title	Symptom Categories
1	Pain & Sensitivity	cold_sensitivity, hot_sensitivity, pressure_pain, spontaneous_pain
2	Gum & Appearance	bleeding_gums, swollen_gums, receding_gums, black_spot, white_spot, yellow_staining
3	Mouth & Habits	bad_breath, dry_mouth, mouth_ulcer, burning_sensation, loose_tooth, broken_tooth
4	Hygiene & Photo	brushes_twice_daily, uses_floss, sugary_diet, acid_exposure + optional photo upload
Step UI Rules:

Show step indicator at top (e.g., "Step 2 of 4")
Each symptom is a YES / NO toggle card (not a checkbox)
Back / Next buttons at the bottom
Final step has a "Submit Assessment" button
Show loading spinner while API call is in progress
4. Result Page (protected)
Header: Risk level badge (LOW / MEDIUM / HIGH) — large and prominent
Section 1 — Conditions Detected: Card per condition with:
Condition name (human-readable, not enum key)
Why it was detected (triggered rules as bullet points)
Explanation text
Section 2 — Recommendations: Timeline-style list of actions with urgency label
Section 3 — Disclaimer: "This is not a medical diagnosis. Consult a licensed dentist."
Button: "View History" | "Start New Assessment"
5. History Page (protected)
List of all past assessments sorted by date (newest first)
Each row: date, risk level badge, conditions detected count
Click row → navigates to the ResultPage for that assessment
Pagination controls (10 per page)
Component Rules
RiskBadge
jsx

// Props: level = "LOW" | "MEDIUM" | "HIGH"
// Renders a colored pill badge
<span className={`risk-badge risk-badge--${level.toLowerCase()}`}>
  {level}
</span>
CSS classes: .risk-badge--low (green), .risk-badge--medium (amber), .risk-badge--high (red)

SymptomToggle
A full-width clickable card showing the symptom label
Selected state: colored border + checkmark icon
Unselected state: subtle gray border
DiagnosisCard
White/surface card with condition name as heading
Bullet list of triggered rules (displayed as plain English, not Prolog predicates)
Soft warning icon next to condition name
RecommendationCard
Urgency label displayed as a colored tag
Action text below
Icon: calendar for scheduled visits, exclamation for urgent
PhotoUpload
Drag-and-drop area with dashed border
Show thumbnail preview after selection
File size and format validation feedback inline
"Remove" button to clear selection
Label: "Upload a mouth photo (optional)"
ProtectedRoute
Wraps routes that require auth
If no JWT in localStorage → redirect to /login
Layout Rules
Max content width: 1100px, centered with margin: 0 auto
Page padding: 1.5rem on mobile, 2.5rem on desktop
Cards use border-radius: 12px and subtle box-shadow
Consistent spacing unit: 0.5rem multiples
Form Validation Rules
Field	Rule
Email	Required, valid email format
Password	Required, min 8 chars
Full Name	Required, max 150 chars
Date of Birth	Optional, must be a past date if provided
Photo	Optional, max 5 MB, JPEG/PNG/WEBP only
Show validation errors only after the user has touched (blurred) the field
On submit, validate all fields and highlight errors before calling API
Navigation Guards
Unauthenticated users → redirect to /login
Authenticated users visiting /login or /register → redirect to /
JWT stored in localStorage as ohas_token
On app load, check token validity (decode and check expiry client-side)
Loading & Error States
Every API call shows a loading spinner on the action button
Disable the button during loading to prevent double-submit
Global error toast for network failures
Inline error messages for form validation failures

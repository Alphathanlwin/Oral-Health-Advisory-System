# Code Standards — Oral Health Advisory System (OHAS)
## Python / FastAPI Standards
### Naming Conventions
|
 Element            
|
 Convention     
|
 Example                         
|
|
--------------------
|
----------------
|
---------------------------------
|
|
 Variables          
|
 snake_case     
|
`risk_level`
, 
`user_id`
|
|
 Functions          
|
 snake_case     
|
`get_assessment_by_id()`
|
|
 Classes            
|
 PascalCase     
|
`AssessmentService`
|
|
 Pydantic Schemas   
|
 PascalCase     
|
`AssessmentCreateRequest`
|
|
 SQLAlchemy Models  
|
 PascalCase     
|
`Assessment`
, 
`User`
|
|
 Enums              
|
 PascalCase     
|
`RiskLevel.HIGH`
|
|
 Constants          
|
 SCREAMING_SNAKE
|
`ACCESS_TOKEN_EXPIRE_MINUTES`
|
|
 Files / Modules    
|
 snake_case     
|
`assessment_service.py`
|
|
 Router prefixes    
|
 kebab-case     
|
`/api/v1/assessments`
|
---
### Dependency Injection
- **ALWAYS** use FastAPI's `Depends()` for injecting services and DB sessions
- **NEVER** use global singletons or module-level state for services
- **NEVER** use field injection (no `self.db = db` as class attribute set in `__init__`)
```python
# ✅ CORRECT
@router.post("/assessments/")
async def create_assessment(
    payload: AssessmentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    assessment_service: AssessmentService = Depends(AssessmentService),
):
    ...
# ❌ WRONG — do not do this
assessment_service = AssessmentService()  # global singleton
```
---
### Pydantic Schemas vs ORM Models
- **ALWAYS** use Pydantic schemas for API request/response bodies
- **NEVER** return SQLAlchemy ORM model instances from endpoints
- Schema files live in `schemas/`, model files live in `models/`
- Use `model_config = ConfigDict(from_attributes=True)` on response schemas
```python
# ✅ CORRECT — response schema
class DiagnosisResponse(BaseModel):
    id: uuid.UUID
    condition: Condition
    explanation: str
    triggered_rules: list[str]
    model_config = ConfigDict(from_attributes=True)
# ❌ WRONG — never return ORM model directly
return db_diagnosis  # do not do this
```
---
### Service Layer Pattern
- All business logic lives in `services/`, **not** in routers
- Routers only: parse request → call service → return response
- Services only: orchestrate logic, call DB, call Prolog, call CV
```python
# router pattern
@router.post("/assessments/", response_model=AssessmentResponse)
async def create_assessment(payload: AssessmentCreateRequest, ...):
    result = await assessment_service.create(payload, current_user.id, db)
    return result
```
---
### Error Handling
- Use FastAPI `HTTPException` for API errors
- Define custom exceptions in `exceptions.py` for domain errors
- All unhandled exceptions should return `500` with a generic message
```python
# exceptions.py
class AssessmentNotFoundException(HTTPException):
    def __init__(self, assessment_id: str):
        super().__init__(status_code=404, detail=f"Assessment {assessment_id} not found")
```
---
### Async Patterns
- Use `async def` for all route handlers and service methods
- Use `await` consistently; never mix sync and async DB calls
- Use `AsyncSession` from SQLAlchemy for all DB operations
---
### File Upload Handling
- Images must be validated before processing:
  - Max size: **5 MB**
  - Allowed types: `image/jpeg`, `image/png`, `image/webp`
  - Minimum resolution: 100×100 px
- Store uploaded files in `backend/uploads/` directory
- Never store raw base64 images in the database — save the file, store the path
---
## React / Frontend Standards
### Component Rules
- **Only** use functional components + hooks (no class components)
- One component per file; filename matches component name
- Component files use `.jsx` extension
```jsx
// ✅ CORRECT
export default function RiskBadge({ level }) {
  ...
}
// ❌ WRONG
class RiskBadge extends React.Component { ... }
```
### Naming Conventions
|
 Element          
|
 Convention  
|
 Example                   
|
|
------------------
|
-------------
|
---------------------------
|
|
 Components       
|
 PascalCase  
|
`DiagnosisCard.jsx`
|
|
 Hooks            
|
 camelCase   
|
`useAssessment()`
|
|
 Variables/State  
|
 camelCase   
|
`currentStep`
, 
`symptoms`
|
|
 API functions    
|
 camelCase   
|
`submitAssessment()`
|
|
 CSS classes      
|
 kebab-case  
|
`.risk-badge--high`
|
### State Management
- Use `useState` and `useContext` (React Context API)
- Global auth state lives in `AuthContext.jsx`
- No Redux; no Zustand (out of scope for this project)
### API Calls
- All API call functions live in `src/api/`
- Use `fetch` or `axios` — be consistent, pick one
- Always handle loading and error states in UI
```jsx
// ✅ CORRECT
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);
async function handleSubmit() {
  setLoading(true);
  try {
    const result = await submitAssessment(payload);
    navigate(`/results/${result.id}`);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
}
```
---
## Prolog Standards
- All rules and facts live in a **single file**: `backend/prolog/knowledge_base.pl`
- Symptom keys must exactly match those defined in `database-schema.md`
- Predicate naming: `snake_case` atoms (e.g., `cold_sensitivity`, `possible(dental_cavity)`)
- Each rule block must have a comment explaining its clinical rationale
```prolog
% ✅ CORRECT — with comments
% Dental cavity is suspected when a visible dark spot is present
% combined with cold sensitivity.
possible(dental_cavity) :-
    symptom(black_spot),
    symptom(cold_sensitivity).
% ❌ WRONG — no comment, unclear predicate name
p(dc) :- s(bs), s(cs).
```
---
## Anti-Patterns to Avoid
|
 Anti-Pattern                              
|
 Why It's Wrong                                     
|
|
-------------------------------------------
|
----------------------------------------------------
|
|
 Returning ORM models from endpoints       
|
 Exposes internal schema, breaks encapsulation      
|
|
 Global service/DB instances               
|
 Not testable, not thread-safe with async           
|
|
 Hardcoding symptom keys in router/service 
|
 Must always reference 
`database-schema.md`
 list    
|
|
 Writing Prolog logic in Python strings    
|
 Logic must live in 
`knowledge_base.pl`
|
|
 Storing passwords in plaintext            
|
 Always hash with bcrypt via passlib                
|
|
 Skipping image validation                 
|
 Could crash CV service or store malicious files    
|

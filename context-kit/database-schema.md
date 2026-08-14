# Database Schema — Oral Health Advisory System (OHAS)
## Database: PostgreSQL 15+
## ORM: SQLAlchemy 2.x (async)
## Migrations: Alembic
---
## Enums
### `RiskLevel`
```
LOW
MEDIUM
HIGH
```
### `Urgency`
```
IMMEDIATE           -- Go to emergency / same day
WITHIN_1_WEEK       -- Book urgent appointment
WITHIN_1_MONTH      -- Book routine appointment
MONITOR_AT_HOME     -- No dentist needed now, maintain hygiene
```
### `Condition`
```
DENTAL_CAVITY
GINGIVITIS
TOOTH_ABSCESS
ENAMEL_EROSION
CANKER_SORES
TOOTH_SENSITIVITY
```
---
## Tables
### `users`
|
 Column         
|
 Type          
|
 Constraints                   
|
 Notes                      
|
|
----------------
|
---------------
|
-------------------------------
|
----------------------------
|
|
 id             
|
 UUID          
|
 PK, default gen_random_uuid() 
|
|
|
 email          
|
 VARCHAR(255)  
|
 UNIQUE, NOT NULL              
|
|
|
 password_hash  
|
 VARCHAR(255)  
|
 NOT NULL                      
|
 bcrypt hash                
|
|
 full_name      
|
 VARCHAR(150)  
|
 NOT NULL                      
|
|
|
 date_of_birth  
|
 DATE          
|
 NULLABLE                      
|
 Optional                   
|
|
 created_at     
|
 TIMESTAMPTZ   
|
 NOT NULL, default NOW()       
|
|
|
 updated_at     
|
 TIMESTAMPTZ   
|
 NOT NULL, default NOW()       
|
 auto-updated on change     
|
---
### `assessments`
|
 Column                
|
 Type          
|
 Constraints                   
|
 Notes                                        
|
|
-----------------------
|
---------------
|
-------------------------------
|
----------------------------------------------
|
|
 id                    
|
 UUID          
|
 PK, default gen_random_uuid() 
|
|
|
 user_id               
|
 UUID          
|
 FK → users.id, NOT NULL       
|
 CASCADE DELETE                               
|
|
 risk_level            
|
 RiskLevel     
|
 NOT NULL                      
|
 Enum: LOW / MEDIUM / HIGH                    
|
|
 photo_urls            
|
 JSONB         
|
 NULLABLE                      
|
 `{"front": "uploads/....jpg", "upper": null, "lower": null}` — each of the 3 guided-capture angles is independently optional (Phase 3D; replaced the single `photo_url VARCHAR` column) 
|
|
 image_analysis_result 
|
 JSONB         
|
 NULLABLE                      
|
 `{"front": <HF response or `{"status":"CV_SERVICE_UNAVAILABLE"}`>, "upper": ..., "lower": ...}` — per-angle raw CV result           
|
|
 created_at            
|
 TIMESTAMPTZ   
|
 NOT NULL, default NOW()       
|
|
---
### `symptom_responses`
Stores the raw symptom questionnaire answers for each assessment.
|
 Column        
|
 Type          
|
 Constraints                   
|
 Notes                                     
|
|
---------------
|
---------------
|
-------------------------------
|
-------------------------------------------
|
|
 id            
|
 UUID          
|
 PK, default gen_random_uuid() 
|
|
|
 assessment_id 
|
 UUID          
|
 FK → assessments.id, NOT NULL 
|
 CASCADE DELETE                            
|
|
 symptom_key   
|
 VARCHAR(100)  
|
 NOT NULL                      
|
 e.g., 
`cold_sensitivity`
, 
`bleeding_gums`
|
|
 value         
|
 BOOLEAN       
|
 NOT NULL                      
|
 Whether symptom is present (true/false)   
|
**Unique constraint**: `(assessment_id, symptom_key)`
---
### `diagnoses`
One row per detected condition within an assessment.
|
 Column          
|
 Type         
|
 Constraints                   
|
 Notes                                           
|
|
-----------------
|
--------------
|
-------------------------------
|
-------------------------------------------------
|
|
 id              
|
 UUID         
|
 PK, default gen_random_uuid() 
|
|
|
 assessment_id   
|
 UUID         
|
 FK → assessments.id, NOT NULL 
|
 CASCADE DELETE                                  
|
|
 condition       
|
 Condition    
|
 NOT NULL                      
|
 Enum: DENTAL_CAVITY, GINGIVITIS, etc.           
|
|
 triggered_rules 
|
 JSONB        
|
 NOT NULL                      
|
 List of Prolog rule names that fired, as JSON   
|
|
 explanation     
|
 TEXT         
|
 NOT NULL                      
|
 Human-readable explanation of why diagnosed     
|
---
### `recommendations`
One row per recommendation, linked to a specific diagnosis.
|
 Column        
|
 Type         
|
 Constraints                   
|
 Notes                                          
|
|
---------------
|
--------------
|
-------------------------------
|
------------------------------------------------
|
|
 id            
|
 UUID         
|
 PK, default gen_random_uuid() 
|
|
|
 diagnosis_id  
|
 UUID         
|
 FK → diagnoses.id, NOT NULL   
|
 CASCADE DELETE                                 
|
|
 action        
|
 TEXT         
|
 NOT NULL                      
|
 e.g., "Visit a dentist within 1 week"          
|
|
 urgency       
|
 Urgency      
|
 NOT NULL                      
|
 Enum: WITHIN_1_WEEK, etc.                      
|
---
## Entity Relationships
```
users
  └──< assessments (one-to-many)
         ├──< symptom_responses (one-to-many)
         └──< diagnoses (one-to-many)
                └──< recommendations (one-to-many)
```
---
## SQLAlchemy Model Conventions
- All models inherit from a `Base` declarative base
- All PKs are UUID generated by PostgreSQL (`server_default=text("gen_random_uuid()")`)
- Use `mapped_column()` and `Mapped[]` typing (SQLAlchemy 2.x style)
- Timestamps use `TIMESTAMP WITH TIME ZONE`
- Enum columns use SQLAlchemy `Enum(PyEnum)` type
### Example Model Pattern
```python
from sqlalchemy import String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import text
from app.models.base import Base
from app.models.enums import RiskLevel
import uuid
class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    risk_level: Mapped[RiskLevel] = mapped_column(SAEnum(RiskLevel), nullable=False)
    photo_urls: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    image_analysis_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # Relationships
    user: Mapped["User"] = relationship(back_populates="assessments")
    symptom_responses: Mapped[list["SymptomResponse"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
    diagnoses: Mapped[list["Diagnosis"]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )
```
---
## Symptom Keys Reference
These are the exact `symptom_key` values used in `symptom_responses` and in Prolog facts.
|
 symptom_key             
|
 Category            
|
 Description                           
|
|
-------------------------
|
---------------------
|
---------------------------------------
|
|
`cold_sensitivity`
|
 Pain/Sensitivity    
|
 Pain when drinking cold liquids       
|
|
`hot_sensitivity`
|
 Pain/Sensitivity    
|
 Pain when drinking hot liquids        
|
|
`pressure_pain`
|
 Pain/Sensitivity    
|
 Pain when biting or chewing           
|
|
`spontaneous_pain`
|
 Pain/Sensitivity    
|
 Pain without any trigger              
|
|
`bleeding_gums`
|
 Gum Issues          
|
 Gums bleed when brushing/flossing     
|
|
`swollen_gums`
|
 Gum Issues          
|
 Gums appear puffy or swollen          
|
|
`receding_gums`
|
 Gum Issues          
|
 Gums pulling away from teeth          
|
|
`black_spot`
|
 Spots/Discoloration 
|
 Dark spot visible on tooth            
|
|
`white_spot`
|
 Spots/Discoloration 
|
 Chalky white area on tooth            
|
|
`yellow_staining`
|
 Spots/Discoloration 
|
 Overall yellow discoloration          
|
|
`bad_breath`
|
 Bad Breath          
|
 Persistent bad breath                 
|
|
`dry_mouth`
|
 Bad Breath          
|
 Mouth feels dry most of the time      
|
|
`mouth_ulcer`
|
 Sores/Ulcers        
|
 Sore lesion inside mouth              
|
|
`burning_sensation`
|
 Sores/Ulcers        
|
 Burning feeling in mouth              
|
|
`loose_tooth`
|
 Structural          
|
 Tooth feels loose                     
|
|
`broken_tooth`
|
 Structural          
|
 Visible crack or broken piece         
|
|
`brushes_twice_daily`
|
 Hygiene Habits      
|
 Brushes at least twice per day        
|
|
`uses_floss`
|
 Hygiene Habits      
|
 Uses dental floss regularly           
|
|
`sugary_diet`
|
 Hygiene Habits      
|
 High sugar/acid in daily diet         
|
|
`acid_exposure`
|
 Hygiene Habits      
|
 Frequent consumption of acidic drinks 
|
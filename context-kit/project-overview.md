# Project Overview — Oral Health Advisory System (OHAS)
## Product Vision
OHAS is a web-based AI-powered oral health advisory system that helps users identify potential dental conditions through a guided symptom questionnaire and an optional mouth photo upload. It uses a **Prolog rule-based expert system** for logical inference and provides **explainable, evidence-backed recommendations** with a clear risk level (Low / Medium / High).
The system does **not** replace a licensed dentist. It advises users on the urgency of seeking professional care and provides educational information about possible conditions.
---
## Academic Context
- **Course**: Artificial Intelligence / Knowledge Representation
- **Concepts demonstrated**:
  - Knowledge representation (Prolog facts and rules)
  - Logical inference (expert-system reasoning)
  - Explainable AI (showing *why* a recommendation was made)
  - Modern Python backend (FastAPI)
  - Optional computer vision (pretrained model via API, no training required)
---
## Target Users
|
 User Type     
|
 Description                                                        
|
|
---------------
|
--------------------------------------------------------------------
|
|
 General Public 
|
 Adults experiencing dental discomfort seeking preliminary guidance 
|
|
 Students       
|
 Evaluators / markers running the system locally                    
|
---
## Core Goals
1. Allow users to register and log in securely
2. Present a structured symptom questionnaire covering 7 categories
3. Optionally accept a mouth photo for visual context
4. Run symptoms through a SWI-Prolog knowledge base to infer possible conditions
5. Produce a risk level (Low / Medium / High) with full explanation of triggered rules
6. Recommend specific actions (e.g., "Visit a dentist within 1 week")
7. Persist all assessments so users can review their history
---
## Diagnosable Conditions (v1 Scope)
|
 Condition          
|
 Key Indicators                                          
|
|
--------------------
|
---------------------------------------------------------
|
|
 Dental Cavity      
|
 Black/brown spot, cold sensitivity, pain on chewing     
|
|
 Gingivitis         
|
 Bleeding gums, swollen gums, bad breath                 
|
|
 Tooth Abscess      
|
 Severe pain, swelling, fever-like sensation, bad taste  
|
|
 Enamel Erosion     
|
 Cold/hot sensitivity, transparent edges, acid exposure  
|
|
 Canker Sores       
|
 Mouth ulcer, burning sensation, white/yellow lesion     
|
|
 Tooth Sensitivity  
|
 Sharp pain with cold/hot, no visible lesion              
|
---
## Symptom Categories Covered
1. Tooth pain / sensitivity (cold, hot, pressure)
2. Gum issues (bleeding, swelling, recession)
3. Visible spots or discoloration (black, white, yellow)
4. Bad breath / dry mouth
5. Mouth sores or ulcers
6. Loose or broken teeth
7. Oral hygiene habits
---
## Risk Level Framework
|
 Level  
|
 Meaning                                        
|
 Example Action                   
|
|
--------
|
------------------------------------------------
|
----------------------------------
|
|
 LOW    
|
 No significant findings, maintain good hygiene 
|
 Brush twice daily, floss         
|
|
 MEDIUM 
|
 Possible early-stage condition                 
|
 See a dentist within 1 month     
|
|
 HIGH   
|
 Likely active condition requiring prompt care  
|
 See a dentist within 1 week      
|
---
## Out of Scope (v1)
- Deep learning model training
- Real-time chat with dentists
- Insurance or billing features
- Mobile native app
- Multi-language support
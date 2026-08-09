# OHAS Agent Context Kit — Master Index
> **Project**: Oral Health Advisory System (OHAS)
> **Stack**: Vite + React · FastAPI · SWI-Prolog · PostgreSQL · JWT
> **Load Order**: When starting a new AI session, load these context files in the order listed below.
> Each file builds on the previous one to give the agent a complete understanding of the OHAS project.
## Context Files (Load in Order)
|
#
|
 File                        
|
 Purpose                                                              
|
|
----
|
-----------------------------
|
----------------------------------------------------------------------
|
|
 1  
|
`project-overview.md`
|
 Product vision, users, goals, domain, academic context               
|
|
 2  
|
`architecture.md`
|
 System layers, data flow, package structure, integration points      
|
|
 3  
|
`database-schema.md`
|
 Full PostgreSQL schema, entities, relationships, enums               
|
|
 4  
|
`code-standards.md`
|
 Python/FastAPI/React conventions, naming rules, patterns             
|
|
 5  
|
`api-standards.md`
|
 REST endpoint design, request/response formats, error handling       
|
|
 6  
|
`library-docs.md`
|
 Key library usage: FastAPI, SQLAlchemy, pyswip, JWT, HuggingFace     
|
|
 7  
|
`ui-rules.md`
|
 React page structure, component rules, layout, UX flows              
|
|
 8  
|
`prolog-kb.md`
|
 Prolog knowledge base design: facts, rules, conditions, risk logic   
|
|
 9  
|
`build-plan.md`
|
 Phased development roadmap and feature sequencing                    
|
|
 10 
|
`progress-tracker.md`
|
 Live development progress per module and feature                     
|
## How to Use This Kit
### Starting a New Session
```
Load context files 1-10 in order before beginning any work.
```
### Before a New Feature
```
1. Review build-plan.md for current phase
2. Review progress-tracker.md for what's done
3. Review architecture.md for where the feature fits
4. Review code-standards.md for how to write it
5. Review api-standards.md if building endpoints
6. Review database-schema.md if touching entities
7. Review prolog-kb.md if touching the knowledge base
```
### After Completing Work
```
1. Update progress-tracker.md with completed items
2. Note any architectural decisions made during the session
```
## Critical Rules for AI Agents
1. **NEVER guess** entity fields, enums, or relationships — always refer to `database-schema.md`
2. **NEVER invent** new architectural layers — follow `architecture.md`
3. **NEVER return** SQLAlchemy models directly — always use Pydantic response schemas
4. **ALWAYS use** constructor/parameter injection in FastAPI via `Depends()`
5. **ALWAYS check** `progress-tracker.md` before starting work to understand current state
6. **NEVER add** Prolog rules or conditions not defined in `prolog-kb.md` without updating it first
7. **ALWAYS validate** image uploads before passing to the CV module
8. **ASK** if uncertain about any design decision rather than assuming
